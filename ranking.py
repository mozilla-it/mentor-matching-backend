import ndjson

from google.cloud import bigquery
bq_client = bigquery.Client()
dataset_name = 'mentoring'
dataset_ref = bq_client.dataset(dataset_name)

from google.cloud import storage
storage_client = storage.Client()
mentoring_bucket = storage_client.get_bucket('dp2-dev-mentoring')


class Ranker():
	
	def safe_cast(self, val, to_type, default=None):
		try:
			return to_type(val)
		except (ValueError, TypeError):
			return default


	def update_bq_table_json(self, uri, fn, table_name, table_schema):
		table_ref = dataset_ref.table(table_name)
		job_config = bigquery.LoadJobConfig()
		job_config.write_disposition = "WRITE_APPEND"  
		job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON

		job_config.autodetect = False
		job_config.schema = table_schema

		orig_rows =  bq_client.get_table(table_ref).num_rows

		load_job = bq_client.load_table_from_uri(uri + fn, table_ref, job_config=job_config)  # API request
		print("Starting job {}".format(load_job.job_id))

		load_job.result()  # Waits for table load to complete.
		destination_table = bq_client.get_table(table_ref)
		print('Loaded {} rows into {}:{}.'.format(destination_table.num_rows-orig_rows, 'mentoring', table_name))

		# move fn to processed folder
		blob = mentoring_bucket.blob(fn)
		new_blob = mentoring_bucket.rename_blob(blob, "processed/" + fn)
		print('Blob {} has been renamed to {}'.format(blob.name, new_blob.name))


	def delimstr_to_set(self, delimstr):
		# parse comma delim availability, expertise, and interests to set
		return set([x.strip() for x in delimstr.split(',')])


	def get_track_level(self, org_level) -> (str, int):
		#org_level = moz.org_level
		if len(org_level) ==2:
			track = org_level[0] 
			level = self.safe_cast(org_level[1], int, 0) 
		else:
			track = ''
			level = 0
		return track, level


	def get_outside_org_score(self, me, other) -> int:
		# outside org 1=prefer, 3=rather not; symmetric for both mentor and learner
		assert me.org is not None, "other " + other.email + " has invalid org value " + other.track
		
		if me.outside_org==1:
			if me.org == other.org:
				return 1
			else:
				return 3
		elif me.outside_org==2:
			if me.org == other.org:
				return 2
			else:
				return 2
		elif me.outside_org==3:
			if me.org == other.org:
				return 3
			else:
				return 1
		else:
			return 2 # default is neutral


	def get_change_track_score(self, learner_track_pref, learner_track, mentor_track) -> int:
		# change career track 1=not interested, 5=very interested => give pref to mentors outside 
		assert mentor_track is not None, "Mentor has invalid track value " + mentor_track
		if learner_track_pref==1:
			if learner_track != mentor_track:
				return 1
			else:
				return 5
		if learner_track_pref==2:
			if learner_track != mentor_track:
				return 2
			else:
				return 4
		if learner_track_pref==3:
			if learner_track != mentor_track:
				return 3
			else:
				return 3
		if learner_track_pref==4:
			if learner_track != mentor_track:
				return 4
			else:
				return 1
		if learner_track_pref==5:
			if learner_track != mentor_track:
				return 5
			else:
				return 1

	
	def P_to_M(self) -> dict:
		return { "P1":"M1",
				"P2":"M1",
				"P3":"M2",
				"P4":"M3",
				"P5":"M4",
				"P6":"M5",
				"P7":"M6",
				"P8":"M6" }


	def M_to_P(self) -> dict:
		return { "M1":"P2",
				"M2":"P3",
				"M3":"P4",
				"M4":"P5",
				"M5":"P6",
				"M6":"P7"}


	def get_career_growth_score(self, learner_interest, learner_track_pref, learner_org_level, mentor_track, mentor_level) -> int:
		assert mentor_track is not None, "Mentor has invalid track value " + mentor_track  
		if ('Technical Leadership' in learner_interest): # or any(s in self.requests for s in self.career_growth_list):
			org_level = learner_org_level
			if learner_track_pref>3: # interested in changing career track, use self.track_equiv
				if org_level[0]=='P':
					org_level = self.P_to_M()[self.track_equiv]
				elif org_level[0]=='M':
					org_level = self.M_to_P()[self.track_equiv]
			track = org_level[0]
			level = self.safe_cast(org_level[1], int, 0)
			if mentor_track==track and mentor_level==level+2:
				return 8
			elif mentor_track==track and mentor_level>level+2:
				return 4
			elif mentor_track==track and mentor_level==level+1:
				return 2
			else:
				return 0
		else:
			return 0


	def rank_mentors(self, learner_email):
		# for learner, update all available mentor rankings in learner_mentor_ranking table
		sql_qry = """DELETE FROM mentoring.learner_mentor_rankings WHERE learner='{}'"""
		query_job = bq_client.query(sql_qry.format(learner_email))
		query_res = query_job.result()  # Waits for job to complete.
		
		# get learner data
		sql_qry = """SELECT * FROM mentoring.learners where email='{}' LIMIT 1"""
		query_job = bq_client.query(sql_qry.format(learner_email))
		learner_obj = query_job.result()  # Waits for job to complete.
		
		learner = []
		for l in learner_obj:
			learner = l
			
		if learner is None:
			print("Ranker.rank_mentors: Learner not found")
			# hmmm exit or remove any such learner from rankings and return err msg?
			return
		
		print(learner.fullname)
		learner_availability = self.delimstr_to_set(learner.availability)
		learner_interest = self.delimstr_to_set(learner.interest)
		learner_track, learner_level = self.get_track_level(learner.org_level)
		
		learner_track_equiv = learner.org_level # default keep same
		if learner_track=='P':
			learner_track_equiv = self.P_to_M()[learner_track_equiv]
		elif learner_track=='M':
			learner_track_equiv = self.M_to_P()[learner_track_equiv]
		print('learner track equiv: ' + learner_track_equiv)
		
		sql_qry = """SELECT m.*, match.mentee_num FROM mentoring.mentors m LEFT JOIN
					(select mentor, count(mentor) as mentee_num from mentoring.matches where status=true group by mentor) match
					on m.email = match.mentor
					"""
		query_job = bq_client.query(sql_qry)
		mentors = query_job.result()  # Waits for job to complete.
		
		json_data=[]
		
		for mentor in mentors:
		
			hard_constraints_met = True
			
			# check mentor limit not hit
			if mentor.mentee_limit == 0:
				hard_constraints_met = False
			if mentor.mentee_num is not None and mentor.mentee_limit is not None:
				if mentor.mentee_limit <= mentor.mentee_num:
					hard_constraints_met = False
				
			# cannot match to themselves
			if learner.email == mentor.email:
				hard_constraints_met = False
		
			# mentor-learner should not be in the same management reporting chain - will need ppl dataset info
			# for now just check that learner's manager = mentor or mentor's manager = learner
			if learner.manager_email == mentor.email or mentor.manager_email == learner.email:
				hard_constraints_met = False
		
			# unless manager says "no", manager approved column has no impact
		
			# If constraints are satisfied, calculate preference rankings for mentors based on feature vector
			if hard_constraints_met:
				score = 0
				
				# get count of overlapping times
				available_times = len(learner_availability.intersection(self.delimstr_to_set(mentor.availability)))
			
				# add bias for requested learner (request input not available from UI for now)
				#if mentor_id==requested_mentor:
				#	#print(self.get_id() + ' requested mentor: ' + requested_mentor)
				#	score = score + 50 # other 50 comes from learner side to make 100 in theory

				if available_times > 0:
					# match interests to expertise, max score of 7
					# need to account for "Other:" somehow
					score = score + len(learner_interest.intersection(self.delimstr_to_set(mentor.expertise)))
					print("interests intersection score:" + str(score))

					score = score + self.get_outside_org_score(learner, mentor)
					
					mentor_track, mentor_level = self.get_track_level(mentor.org_level)
					score = score + self.get_change_track_score(learner.change_track, learner_track, mentor_track)

					# option to constrain mentor org level > learner org level? do levels translate across M/P?
					score = score + self.get_career_growth_score(learner_interest, learner.change_track, learner.org_level, mentor_track, mentor_level)

					# so far learner ranks range is [2,18] + 8 career growth + female pref 8 + racial pref? + remotee?
					#score = score + self.get_requests_score(learner, mentor)

					# be careful matching those in relationship/married/dating/familial - no available attribute
					
				print('mentor: ' + mentor.email + ', score: ' + str(score))
				if score > 0:
					# add or update learner mentor ranking to table
					print("add or update rankings to learner_mentor_rankings")
					json_data.append({'learner':learner_email,'mentor':mentor.email,'ranking':score})
					#json_data.append(dict(zip(row_headers,row)))
					
		fn = 'learner_mentor_rankings.json'
		with open("/tmp/" + fn, 'w') as f:
			ndjson.dump(json_data, f) #, indent=4) # convert datetime to utc and format as str
		blob = mentoring_bucket.blob(fn)
		blob.upload_from_filename("/tmp/" + fn)
		schema = [ bigquery.SchemaField('learner', 'STRING', mode='NULLABLE'),
					bigquery.SchemaField('mentor', 'STRING', mode='NULLABLE'),
					bigquery.SchemaField('ranking', 'INTEGER', mode='NULLABLE'),
					]
		self.update_bq_table_json("gs://dp2-dev-mentoring/", fn, "learner_mentor_rankings", schema)


	def rank_learners(self, mentor_email):
		# for mentor, update all available learner rankings in mentor_learner_ranking table
		sql_qry = """DELETE FROM mentoring.mentor_learner_rankings WHERE mentor='{}'"""
		query_job = bq_client.query(sql_qry.format(mentor_email))
		query_res = query_job.result()  # Waits for job to complete.
		
		# get mentor data with any matched pairs including mentor limit
		sql_qry = """SELECT * FROM (
					(SELECT * FROM mentoring.mentors where email='{}') m LEFT JOIN
					(select mentor, count(mentor) as mentee_num from mentoring.matches where status=true group by mentor) match
					on m.email = match.mentor
					) LIMIT 1
					"""
		query_job = bq_client.query(sql_qry.format(mentor_email))
		mentor_obj = query_job.result()  # Waits for job to complete.
		
		mentor = []
		for m in mentor_obj:
			mentor = m
			
		if mentor is None:
			print("Ranker.rank_learners: Mentor not found")
			return
		
		print(mentor.fullname)
		mentor_availability = self.delimstr_to_set(mentor.availability)
		mentor_expertise = self.delimstr_to_set(mentor.expertise)
		mentor_track, mentor_level = self.get_track_level(mentor.org_level)
		
		sql_qry = """SELECT * FROM mentoring.learners"""
		query_job = bq_client.query(sql_qry)
		learners = query_job.result()  # Waits for job to complete.
		
		json_data=[]
		
		for learner in learners:
		
			hard_constraints_met = True
			
			# check mentor limit not hit
			if mentor.mentee_limit == 0:
				hard_constraints_met = False
			if mentor.mentee_num is not None and mentor.mentee_limit is not None:
				if mentor.mentee_limit <= mentor.mentee_num:
					hard_constraints_met = False
				
			# cannot match to themselves
			if mentor_email == learner.email:
				hard_constraints_met = False
		
			# mentor-learner should not be in the same management reporting chain - will need ppl dataset info
			# for now just check that learner's manager = mentor or mentor's manager = learner
			if learner.manager_email == mentor_email or mentor.manager_email == learner.email:
				hard_constraints_met = False

			# unless manager says "no", manager approved column has no impact

			# If constraints are satisfied, calculate preference rankings for mentors based on feature vector
			if hard_constraints_met:
				score = 0

				# get count of overlapping times
				available_times = len(mentor_availability.intersection(self.delimstr_to_set(learner.availability)))

				# add bias for requested learner (request input not available from UI for now)
				#if mentor_id==requested_mentor:
				#	#print(self.get_id() + ' requested mentor: ' + requested_mentor)
				#	score = score + 50 # other 50 comes from learner side to make 100 in theory

				if available_times > 0:
					# match interests to expertise, max score of 7
					# need to account for "Other:" somehow
					score = score + len(mentor_expertise.intersection(self.delimstr_to_set(learner.interest)))
					print("expertise intersection score:" + str(score))

					score = score + self.get_outside_org_score(mentor, learner)

					# so far learner ranks range is [2,18] + 8 career growth + female pref 8 + racial pref? + remotee?
					#score = score + self.get_requests_score(learner, mentor)

					# be careful matching those in relationship/married/dating/familial - no available attribute
					
				print('learner: ' + learner.email + ', score: ' + str(score))
				if score > 0:
					# add or update learner mentor ranking to table
					print("add or update rankings to mentor_learner_rankings")
					json_data.append({'mentor':mentor_email,'learner':learner.email,'ranking':score})
					
		fn = 'mentor_learner_rankings.json'
		with open("/tmp/" + fn, 'w') as f:
			ndjson.dump(json_data, f) #, indent=4) # convert datetime to utc and format as str
		blob = mentoring_bucket.blob(fn)
		blob.upload_from_filename("/tmp/" + fn)
		schema = [ bigquery.SchemaField('mentor', 'STRING', mode='NULLABLE'),
					bigquery.SchemaField('learner', 'STRING', mode='NULLABLE'),
					bigquery.SchemaField('ranking', 'INTEGER', mode='NULLABLE'),
					]
		self.update_bq_table_json("gs://dp2-dev-mentoring/", fn, "mentor_learner_rankings", schema)


def main():
	naiveranker = Ranker()
	

if __name__ == '__main__':
	main()

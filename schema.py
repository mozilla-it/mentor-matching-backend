import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from database import db_session
from models import Mentor as MentorModel
from models import Learner as LearnerModel
from models import MentorLearnerRankings as MentorLearnerRankingsModel
from models import LearnerMentorRankings as LearnerMentorRankingsModel
from ranking import Ranker as NaiveRanker
from sqlalchemy import and_
	    
class Mentors(SQLAlchemyObjectType):
	class Meta:
	    model = MentorModel
	    interfaces = (relay.Node, )
	    
class Learners(SQLAlchemyObjectType):
	class Meta:
	    model = LearnerModel
	    interfaces = (relay.Node, )
	    
class MentorLearnerRankings(SQLAlchemyObjectType):
	class Meta:
	    model = MentorLearnerRankingsModel
	    interfaces = (relay.Node, )
	    
class LearnerMentorRankings(SQLAlchemyObjectType):
	class Meta:
	    model = LearnerMentorRankingsModel
	    interfaces = (relay.Node, )


# Used to Create New Mentor
class createOrUpdateMentor(graphene.Mutation):
	class Input:
		email = graphene.String(required=True)
		ts = graphene.String(required=True)
		role = graphene.String(required=True)
		availability = graphene.String(required=True) # comma delim list of enum hours in UTC
		org_level = graphene.String(required=False, default_value='') # get this from cis
		org = graphene.String(required=True)
		expertise = graphene.String(required=True) # comma delim list of enum
		outside_org = graphene.Int(required=True)
		requests = graphene.String(required=False, default_value='') # not in current scope
		identify_as = graphene.String(required=False, default_value='') # not in current scope
		full_name = graphene.String(required=True)
		manager_email = graphene.String(required=False, default_value='') # get this from cis
		#welcome_email_date = graphene.String(required=False, default_value=0) # update api
		#manager_approval_email_date = graphene.String(required=False, default_value=0) # update api
		#manager_approved_date = graphene.String(required=False, default_value=0) # not part of api
		#mentee_limit = graphene.Int(required=False, default_value=2)
		#gender = graphene.String(required=False, default_value='') # get this from cis

	ok = graphene.Boolean()
	mentor = graphene.Field(Mentors)
	rankings = graphene.Field(MentorLearnerRankings)

	@classmethod
	def mutate(cls, _, args, context, info):
		query = Mentors.get_query(context)
		mentor = query.filter(MentorModel.email == args.get('email')).first()

		if mentor is None:
			mentor = MentorModel(email=args.get('email'), 
		                     timestamp=args.get('ts'),
		                     role=args.get('role'),
		                     availability=args.get('availability'),
		                     org_level=args.get('org_level'),
		                     org=args.get('org'),
		                     expertise=args.get('expertise'),
		                     outside_org=args.get('outside_org'),
		                     requests=args.get('requests'),
		                     identify_as=args.get('identify_as'),
		                     fullname=args.get('full_name'),
		                     manager_email=args.get('manager_email'),
		                     #Sent_Wecome_Email__date_=args.get('welcome_email_date'),
		                     #Sent_Manager_Approval_Email__date_=args.get('manager_approval_email_date'),
		                     #Manager_Approved__date_=args.get('manager_approved_date'),
		                     #Mentee_Limit=args.get('mentee_limit'),
		                     #Gender=args.get('gender'),
		                     )
			db_session.add(mentor)
		else:
			mentor.timestamp=args.get('ts')
			mentor.role=args.get('role')
			mentor.availability=args.get('availability')
			mentor.org_level=args.get('org_level')
			mentor.org=args.get('org')
			mentor.expertise=args.get('expertise')
			mentor.outside_org=args.get('outside_org')
			mentor.requests=args.get('requests')
			mentor.identify_as=args.get('identify_as')
			mentor.fullname=args.get('full_name')
			mentor.manager_email=args.get('manager_email')

		db_session.commit()
		
		# on successful commit, compute ranking and update or overwrite in rankings table
		rankings = MentorLearnerRankingsModel(mentor=args.get('email'), 
		                     learner='testlearner2',
		                     ranking=NaiveRanker.rank_learners(args.get('email')))
		db_session.add(rankings)
		db_session.commit()
		
		ok = True
		return createOrUpdateMentor(mentor=mentor, rankings=rankings, ok=ok)


# Used to Create New Learner and return matches
class createOrUpdateLearner(graphene.Mutation):
	class Input:
		email = graphene.String(required=True)
		ts = graphene.String(required=True)
		role = graphene.String(required=True)
		availability = graphene.String(required=True) # comma delim list of enum hours in UTC
		org_level = graphene.String(required=False, default_value='') # get this from cis
		org = graphene.String(required=True) # can't enum cause of Other input field
		interest = graphene.String(required=True) # comma delim list of enum
		change_track = graphene.Int(required=True)
		outside_org = graphene.Int(required=True)
		requests = graphene.String(required=False, default_value='') # not in current scope
		identify_as = graphene.String(required=False, default_value='') # not in current scope
		full_name = graphene.String(required=True)
		manager_email = graphene.String(required=False, default_value='') # get this from cis
		#welcome_email_date = graphene.String(required=False, default_value=0) # update api
		#manager_approval_email_date = graphene.String(required=False, default_value=0) # update api
		#manager_approved_date = graphene.String(required=False, default_value=0) # not part of api
		#mentee_limit = graphene.Int(required=False, default_value=2)
		#gender = graphene.String(required=False, default_value='') # get this from cis

	ok = graphene.Boolean()
	learner = graphene.Field(Learners)
	rankings = graphene.Field(LearnerMentorRankings)

	@classmethod
	def mutate(cls, _, args, context, info):
	
		query = Learners.get_query(context)
		learner = query.filter(LearnerModel.email == args.get('email')).first()

		if learner is None:
			learner = LearnerModel(email=args.get('email'), 
		                     timestamp=args.get('ts'),
		                     role=args.get('role'),
		                     availability=args.get('availability'),
		                     org_level=args.get('org_level'),
		                     org=args.get('org'),
		                     interest=args.get('interest'),
		                     change_track=args.get('change_track'),
		                     outside_org=args.get('outside_org'),
		                     requests=args.get('requests'),
		                     identify_as=args.get('identify_as'),
		                     fullname=args.get('full_name'),
		                     manager_email=args.get('manager_email'),
		                     #Sent_Wecome_Email__date_=args.get('welcome_email_date'),
		                     #Sent_Manager_Approval_Email__date_=args.get('manager_approval_email_date'),
		                     #Manager_Approved__date_=args.get('manager_approved_date'),
		                     #Mentee_Limit=args.get('mentee_limit'),
		                     #Gender=args.get('gender'),
		                     )
			db_session.add(learner)
		else:
			learner.timestamp=args.get('ts')
			learner.role=args.get('role')
			learner.availability=args.get('availability')
			learner.org_level=args.get('org_level')
			learner.org=args.get('org')
			learner.interest=args.get('interest')
			learner.change_track=args.get('change_track')
			learner.outside_org=args.get('outside_org')
			learner.requests=args.get('requests')
			learner.identify_as=args.get('identify_as')
			learner.fullname=args.get('full_name')
			learner.manager_email=args.get('manager_email')
		db_session.commit()
		
		# on successful commit, compute ranking and update or overwrite in rankings table
		rankings = LearnerMentorRankingsModel(learner=args.get('email'), 
		                     mentor='testmentor2',
		                     ranking=NaiveRanker.rank_mentors(args.get('email')))
		db_session.add(rankings)
		db_session.commit()
		
		# return top 3 rankings for learner
		
		ok = True
		return createOrUpdateLearner(learner=learner, rankings=rankings, ok=ok)
		

class Query(graphene.ObjectType):
	node = relay.Node.Field()

	mentor = SQLAlchemyConnectionField(Mentors)
	find_mentor = graphene.Field(lambda: Mentors, email = graphene.String())
	#get_mentor_matches = 

	def resolve_find_mentor(self,args,context,info):
		query = Mentors.get_query(context)
		email = args.get('email')
		# you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
		return query.filter(MentorModel.email == email).first()

	learner = SQLAlchemyConnectionField(Learners)
	find_learner = graphene.Field(lambda: Learners, email = graphene.String())
	#get_learner_matches = 

	def resolve_find_learner(self,args,context,info):
		query = Learners.get_query(context)
		email = args.get('email')
		# you can also use and_ with filter() eg: filter(and_(param1, param2)).first()
		return query.filter(LearnerModel.email == email).first()

	all_mentor_rankings = SQLAlchemyConnectionField(MentorLearnerRankings)
	find_mentor_rankings = graphene.Field(lambda: graphene.List(MentorLearnerRankings), mentor = graphene.String())

	def resolve_find_mentor_rankings(self,args,context,info):
		query = MentorLearnerRankings.get_query(context)
		mentor_email = args.get('mentor')
		# you can also use and_ with filter() eg:  filter(and_(param1, param2)).first()
		return query.filter(MentorLearnerRankingsModel.mentor == mentor_email).all()

	all_learner_rankings = SQLAlchemyConnectionField(LearnerMentorRankings)
	find_learner_rankings = graphene.Field(lambda: graphene.List(LearnerMentorRankings), learner = graphene.String())

	def resolve_find_learner_rankings(self,args,context,info):
		query = LearnerMentorRankings.get_query(context)
		learner_email = args.get('learner')
		# you can also use and_ with filter() eg:  filter(and_(param1, param2)).first()
		return query.filter(LearnerMentorRankingsModel.learner == learner_email).all()


class MyMutations(graphene.ObjectType):
	create_or_update_mentor = createOrUpdateMentor.Field()
	create_or_update_learner = createOrUpdateLearner.Field()

schema = graphene.Schema(query=Query, mutation=MyMutations, types=[Mentors, Learners])

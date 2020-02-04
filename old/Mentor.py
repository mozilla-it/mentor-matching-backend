from .Mozillian import Mozillian
from .util import safe_cast
from datetime import  datetime
from sortedcontainers import SortedDict
from operator import neg

class Mentor(Mozillian):

  def __init__(self, row):
    super().__init__(row) #row['Email Address'], row['Organizational level (i.e. P3, M2, etc.)'], row['Organization'], row['Participant full name'], row['Manager email'])
    self.submitted_dt = row['Timestamp']
    self.time_availability_to_set(row['Time Availability'])
    self.expertise_to_set(row['Areas of expertise'])
    # if missing outside_org value, set to unbias value of 2
    self.outside_org = safe_cast(row['Interest in mentoring or learning from someone outside your own organization?'], int, 2)
    assert self.outside_org in [1,2,3], self.get_id() + " has invalid outside_org value " + str(self.outside_org)
    self.requests = row['Any particular requests?']
    self.identify_as = row['Do you identify yourself as']
    self.welcome_email_dt = row['Sent Wecome Email (date)']
    self.notify_manager_dt = row['Sent Manager Approval Email (date)']
    self.manager_approved_dt = row['Manager Approved (date)']
    self.mentee_limit = safe_cast(row['Mentee Limit'], int, 2) # by default mentors have a max of two mentees
        
        
  def time_availability_to_set(self, availability):
    """ Set times person is available in set form """
    self.availability_set = set([x.strip() for x in availability.split(',')])

        
  def expertise_to_set(self, expertise):
    """ Set person's  expertise in set form """
    self.expertise_set = set([x.strip() for x in expertise.split(',')])

        
  def get_submitted_dt(self) -> datetime:
    return self.submitted_dt


  def get_expertise(self) -> set:
    return self.expertise_set

        
  def get_times_available(self) -> set:
    return self.availability_set


  def get_mentee_limit(self) -> int:
    return self.mentee_limit
    

  def set_mentee_limit(self, mentee_limit:int):
    self.mentee_limit = mentee_limit


  def get_outside_org_score(self, learner) -> int:
    # outside org 1=prefer, 3=rather not
    assert learner.org is not None, "Learner " + learner.get_id() + " has invalid org value " + learner.track
    if self.outside_org==1:
      if self.org == learner.org:
        return 1
      else:
        return 3
    elif self.outside_org==2:
      if self.org == learner.org:
        return 2
      else:
        return 2
    elif self.outside_org==3:
      if self.org == learner.org:
        return 3
      else:
        return 1
        

  def calc_score(self, learner, is_requested):
    # get count of overlapping times
    available_times = len(self.availability_set.intersection(learner.get_times_available()))

    # If constraints are satisfied, calculate preference rankings for learners based on feature vector
    score = 0
      
    # add bias for requested mentor
    if is_requested:
      score = score + 50
        
    if available_times > 0:
      # match expertise to interest, max score of 7
      # need to account for "Other:" somehow
      score = score + len(self.expertise_set.intersection(learner.get_interests()))

      score = score + self.get_outside_org_score(learner)

    return score
            

  def set_preferences(self, learners):
    self.preferences = SortedDict(neg) #, enumerate('abc', start=1))

    for learner in learners:
      # Filter on constraints    	
      # cannot match to themselves
      if self.get_id() == learner.get_id():
        continue
      # mentor-learner should not be in the same management reporting chain - will need ppl dataset info
      # for now just check that learner's manager = mentor
      if self.get_manager_email() == learner.get_id():
        continue

      # unless manager says "no", manager approved column has no impact
   
      # get count of overlapping times
      available_times = len(self.availability_set.intersection(learner.get_times_available()))

      # If constraints are satisfied, calculate preference rankings for learners based on feature vector
      score = 0
      if available_times > 0:

        # match expertise to interest, max score of 7
        # need to account for "Other:" somehow
        score = score + len(self.expertise_set.intersection(learner.get_interests()))
        #print("interests intersection score:" + str(score))

        # outside org 1=prefer, 3=rather not
        # add 1 if prefer and orgs not the same
        if self.outside_org==1 and self.org != learner.org:
          #print("outside org add 1: " + mentor_org)
          score = score + 1
        # add 1 if rather not and orgs are the same
        if self.outside_org==3 and self.org == learner.org:
          #print("outside org add 1: " + mentor_org)
          score = score + 1

        # so far ranks range is [0,8]

        # be careful matching those in relationship/married/dating/familial - How??

        # option to constrain mentor org level > learner org level?

        # if score is the same, order by date_submitted? no i think this is used in the apposite & global draw 
        #print(mentor.get_id() + ": " + str(score))
        
        if score > 0:
          if self.preferences.__contains__(score):
            self.preferences[score].append(learner)
          else:
            self.preferences[score] = [learner]

  def set_preferences_subscribed(self, subscribed_learners:dict, requested_learner=""):
    self.preferences = SortedDict(neg) #, enumerate('abc', start=1))
    self.learner_score = {}

    for subscribed_learner_id, subscribed_learner in subscribed_learners.items():
      # Filter on constraints    	
      # cannot match to themselves
      if self.get_id() == subscribed_learner_id:
        continue
      # mentor-learner should not be in the same management reporting chain - will need ppl dataset info
      # for now just check that learner's manager = mentor
      if self.get_manager_email() == subscribed_learner_id or subscribed_learner.get_manager_email() == self.get_id():
        continue

      # unless manager says "no", manager approved column has no impact
   
      # get count of overlapping times
      available_times = len(self.availability_set.intersection(subscribed_learner.get_times_available()))

      # If constraints are satisfied, calculate preference rankings for learners based on feature vector
      score = 0
      
      # add bias for requested mentor
      if subscribed_learner_id==requested_learner:
        print(self.get_id() + ' requested learner: ' + requested_learner)
        score = score + 50
        
      if available_times > 0:

        # match expertise to interest, max score of 7
        # need to account for "Other:" somehow
        score = score + len(self.expertise_set.intersection(subscribed_learner.get_interests()))
        #print("interests intersection score:" + str(score))

        score = score + self.get_outside_org_score(subscribed_learner)

        # so far ranks range is [2,13]

        # be careful matching those in relationship/married/dating/familial - How??

        # option to constrain mentor org level > learner org level? do levels translate across M/P?

        # if score is the same, order by date_submitted? no i think this is used in the apposite & global draw 
        #print(mentor.get_id() + ": " + str(score))
        
        #if score > 0:
      if self.preferences.__contains__(score):
        self.preferences[score].append(subscribed_learner)
      else:
        self.preferences[score] = [subscribed_learner]
          
      self.learner_score[subscribed_learner_id] = score


  def get_preferences(self) -> SortedDict:
    return self.preferences
    
  def get_ranked_learners(self) -> list:
    ranked_learners = []
    # add weights to those scores that are the same?
    for value in self.preferences.values():
      ranked_learners.extend([x.get_id() for x in value])
    
    #for score, learners_list in self.preferences.items():
    #  print("score: " + str(score) + ", learners: " + ','.join([x.get_id() for x in learners_list]))
    
    return ranked_learners
    
  def get_learner_score(self) -> dict:
    return self.learner_score


  def get_learner_rank(self, learner, is_requested) -> int:
    #scores = [score for subscribed_learner_id, score in self.learner_score.items() if subscribed_learner_id == learner.get_id()]
    return self.calc_score(learner, is_requested)
        

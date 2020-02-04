from .Learner import Learner
from .Mentor import Mentor

class Pair():

  def __init__(self, mentor=None, learner=None, is_requested=False):
    self.mentor = mentor
    self.learner = learner
    self.is_requested_pair = is_requested
    
    if isinstance(self.mentor, Mentor) and isinstance(self.learner, Learner):
      self.score = self.mentor.get_learner_rank(learner, is_requested) + self.learner.get_mentor_rank(mentor, is_requested)
    else:
      self.score = 0
  

  def get_mentor_id(self) -> str:
    if self.mentor is None:
      return ""
    else:
      return self.mentor.get_id()
    

  def get_learner_id(self) -> str:
    if self.learner is None:
      return ""
    else:
      return self.learner.get_id()
 
 
  def get_mentor_org_level(self) -> str:
    if self.mentor is None:
      return ""
    else:
      return self.mentor.get_org_level()
    

  def get_learner_org_level(self) -> str:
    if self.learner is None:
      return ""
    else:
      return self.learner.get_org_level()   

  
  def get_score(self) -> int:
    return self.score


  def set_is_requested_pair(self, is_requested:bool):
    self.is_requested_pair = is_requested


  def get_is_requested_pair(self) -> bool:
    return self.is_requested_pair

import pandas as pd
import csv
from .Learner import Learner
from .Mentor import Mentor
from .Pair import Pair
from matching import Player
from matching.games import HospitalResident, StableMarriage
from pathlib import Path


# read data/Learners.tsv and return dictionary of Learners
def load_learners() -> dict:

  base_path = Path(__file__).parent
  file_path = (base_path / "../data/Learners.tsv").resolve()

  learners = dict()
  with open(file_path) as tsvfile:
    reader = csv.DictReader(tsvfile, dialect='excel-tab')
    for row in reader:
      learner = Learner(row)
      learner_id = learner.get_id()
      if learner_id in learners:
        print("Duplicate key for Learner " + learner_id + "not added")
      else:     
        learners[learner_id] = learner
  return learners
  

# read data/Mentors.tsv and return dictionary of Mentors
def load_mentors() -> dict:
  base_path = Path(__file__).parent
  file_path = (base_path / "../data/Mentors.tsv").resolve()

  mentors = dict()
  with open(file_path) as tsvfile:
    reader = csv.DictReader(tsvfile, dialect='excel-tab')
    for row in reader:
      mentor = Mentor(row)
      mentor_id = mentor.get_id()
      if mentor_id in mentors:
        print("Duplicate key for Mentor " + mentor_id + "not added")
      else:
        mentors[mentor_id] = mentor      
  return mentors
  
  
# go through learners list and decrement mentor limit/availability; remove any mentors with 0 mentee limit
def update_mentors(mentors: dict, learners: dict) -> (dict, dict):
  #if learner has pairing, find in mentors and decrement Mentee Limit
  
  for learner_id, learner in list(learners.items()):
    if learner.get_mentor():
      print('Remove learner ' + learner_id + ' has mentor ' + learner.get_mentor())
      del learners[learner_id]
      mentors[learner.get_mentor()].set_mentee_limit(mentors[learner.get_mentor()].get_mentee_limit() - 1)

  mentors = { mentor_id : mentor for mentor_id, mentor in mentors.items() if mentor.get_mentee_limit() > 0 }
  #print(mentors.keys())

  return mentors, learners
  

# pairing should pair all learners unless there is no matching time availability
# mentor may have have more than one learner or no learners
def run_pairing(mentors, learners, requested_pairings_learners, requested_pairings_mentors):

  learners_left = list(learners.keys())
  #mentors_left = list(mentors.keys())
  once_more = True
  
  pairings = []

  while once_more:
    if len(learners) < len(mentors):
      once_more = False
    
    learner_prefs = {}
    # check for if no matches after contraints satisfied, then soften constraint (allow more mentors?)
    for learner_id, learner in learners.items():
      #if learner.get_id() == "jlund@mozilla.com":
      is_requested = False
      if learner_id in requested_pairings_learners:
        is_requested = True
        #print("jlund requested " + requested_pairings_mentors[requested_pairings_learners.index(learner_id)])
        learner.set_preferences(mentors, requested_pairings_mentors[requested_pairings_learners.index(learner_id)])
      else:
        learner.set_preferences(mentors)
      lprefs = learner.get_preferences()

      if len(lprefs) == 0:
        #rerun with softened contraints
        pairings.append(Pair(learner=learner, is_requested=is_requested))
        learners_left.remove(learner_id)
        print("learner " + learner_id + " has no matching preferences.")
        continue
      # put learner prefs into dictionary for matching
      learner_prefs[learner_id] = learner.get_ranked_mentors()

    mentor_prefs = {}
    for mentor_id, mentor in mentors.items():
      #if learner.get_id() == "kmoir@mozilla.com":
      # get all learners in learner_prefs that have mentor in their values list
      subscribed_learner_ids = [k for k,v in learner_prefs.items() if mentor_id in v]
      subscribed_learners = {id: learners[id] for id in subscribed_learner_ids}
      
      is_requested = False
      if mentor_id in requested_pairings_mentors:
        is_requested = True
        mentor.set_preferences_subscribed(subscribed_learners, requested_pairings_learners[requested_pairings_mentors.index(mentor_id)])
      else:
        mentor.set_preferences_subscribed(subscribed_learners)
      mprefs = mentor.get_preferences()
      if len(mprefs) == 0:
        #rerun with softened contraints
        #pairings.append(Pair(mentor=mentor))
        print("mentor " + mentor.get_id() + " has no matching preferences.")
        continue
      # put learner prefs into dictionary for matching
      mentor_prefs[mentor.get_id()] = mentor.get_ranked_learners()

    capacities = {m: 1 for m in mentor_prefs}
    game = HospitalResident.create_from_dictionaries(learner_prefs, mentor_prefs, capacities)
    matching = game.solve()

    for k,v in matching.items():
      if len(v) > 0:
        if k.name in requested_pairings_learners or v[0].name in requested_pairings_learners:
          pairings.append(Pair(mentor=mentors[k.name], learner=learners[v[0].name], is_requested=True))
        else:
          pairings.append(Pair(mentor=mentors[k.name], learner=learners[v[0].name])) # assumes capacity is 1
        learners_left.remove(v[0].name)
      #else:
      #  pairings.append(Pair(mentor=mentors[k.name]))

    # list unpaired learners
    learners = {k: learners[k] for k in learners_left}

  return pairings


mentors = load_mentors()

learners = load_learners()

# update mentors list: decrement if pairing exists and remove any with 0 limit
mentors, learners = update_mentors(mentors, learners) 
print(len(mentors))
print(len(learners))

# read in file of pre-matched pairs Learner, Mentor
requested_pairings = {'tvyas@mozilla.com':'stpeter@mozilla.com',
                      'ealvarez@mozilla.com':'mthomson@mozilla.com',
                      'jlund@mozilla.com':'aoverholt@mozilla.com',
                      'smcgahan@mozilla.com':'rdalal@mozilla.com',
                      'jlorenzo@mozilla.com':'leplatrem@mozilla.com'}
requested_pairings_learners = list(requested_pairings.keys())
requested_pairings_mentors = list(requested_pairings.values())

pairings = run_pairing(mentors, learners, requested_pairings_learners, requested_pairings_mentors)

# check all learners have been paired
print("length of paired learners : " + str(len([o.get_learner_id() for o in pairings])))
print("length of unique paired learners : " + str(len(set([o.get_learner_id() for o in pairings]))))
print("length of learners :" + str(len(learners)))

paired_mentors = set([o.get_mentor_id() for o in pairings])
unpaired_mentors = set(mentors.keys()).difference(paired_mentors)
print(unpaired_mentors)

# add any mentors w/o learners
for mentor in unpaired_mentors: 
  # update mentors list: decrement if paired and remove any with 0 limit
  pairings.append(Pair(mentor=mentors[mentor]))
  
print("length of paired mentors : " + str(len([o.get_mentor_id() for o in pairings])))
print("length of unique paired mentors : " + str(len(set([o.get_mentor_id() for o in pairings])))) # maybe +1 for learner unmatchable due to time availability
print("length of mentors :" + str(len(mentors)))

# match score will have to be some average or sum of both learner and mentor scores normalized by whole group
# score game penalize for learner - mentor score diff from optimal match (nah, should already be account for in each side)
# every matched attribute is one unit (equivalence across attribute matches) - can add weighting later
# use additive model implies trade off units has fixed exchange rate

# in place sort pairings list by mentor
pairings.sort(key=lambda x: x.get_mentor_id())
print("Mentor, Mentee, Score, Score(%)")
for p in pairings:
  print(p.get_mentor_id() + ", " + p.get_learner_id() + ", " + str(min(p.get_score(), 100)) + ", " + str(min(p.get_score()/31.0*100,100)))


# provide pairings formatted as Learner Name	Learner Email	Mentor Name	Mentor Email
print("Learner Name, Learner Email, Mentor Name, Mentor Email")
for p in pairings:
  row = ""
  try:  
    row = row + learners[p.get_learner_id()].full_name + ", " + p.get_learner_id() + ", " + p.get_learner_org_level()
  except KeyError:
    row = row + "N/A, N/A" 
  try:  
    row = row + ", " + mentors[p.get_mentor_id()].full_name + ", " + p.get_mentor_id() + ", " + p.get_mentor_org_level()
  except KeyError:
    row = row + ", N/A, N/A" 
  print(row)


learner_ids = list(sorted(learners.keys())) # should preserve order
mentor_ids = list(sorted(mentors.keys()))

# print the matrix of Scores from Mentor to Learner
header_row = "ids"
for learner_id in learner_ids:
  header_row = header_row + ", " + learner_id
print(header_row)
for mentor_id in mentor_ids: #, mentor in mentors.items():
  row_str = mentor_id
  for learner_id in learner_ids:
    if learner_id in requested_pairings_learners:
      if requested_pairings[learner_id] == mentor_id:
        learner_score = mentors[mentor_id].get_learner_rank(learners[learner_id], True)
      else:
        learner_score = mentors[mentor_id].get_learner_rank(learners[learner_id], False)
    else:
      learner_score = mentors[mentor_id].get_learner_rank(learners[learner_id], False)
    row_str = row_str + ", " + str(learner_score)
  print(row_str)
  
  
# print the matrix of Scores from Learner to Mentor
header_row = "ids"
for mentor_id in mentor_ids:
  header_row = header_row + ", " + mentor_id
print(header_row)
for learner_id in learner_ids: #, mentor in mentors.items():
  row_str = learner_id
  for mentor_id in mentor_ids:
    if learner_id in requested_pairings_learners:
      if requested_pairings[learner_id] == mentor_id:
        mentor_score = learners[learner_id].get_mentor_rank(mentors[mentor_id], True)
      else:
        mentor_score = learners[learner_id].get_mentor_rank(mentors[mentor_id], False)
    else:
      mentor_score = learners[learner_id].get_mentor_rank(mentors[mentor_id], False)
        
    row_str = row_str + ", " + str(mentor_score)
  print(row_str)


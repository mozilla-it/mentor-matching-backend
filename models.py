from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, String, Date, func
from sqlalchemy.orm import backref, relationship


class Mentor(Base):
	__tablename__ = 'mentors'
	email = Column(Text, primary_key=True)
	timestamp = Column(DateTime)
	role = Column(Text)
	availability = Column(Text)
	org_level = Column(Text)
	org = Column(Text)
	expertise = Column(Text)
	outside_org = Column(Integer)
	requests = Column(Text)
	identify_as = Column(Text)
	fullname = Column(Text)
	manager_email = Column(Text)


class Learner(Base):
	__tablename__ = 'learners'
	email = Column(Text, primary_key=True)
	timestamp = Column(DateTime)
	role = Column(Text)
	availability = Column(Text)
	org_level = Column(Text)
	org = Column(Text)
	interest = Column(Text)
	change_track = Column(Text)
	outside_org = Column(Integer)
	requests = Column(Text)
	identify_as = Column(Text)
	fullname = Column(Text)
	manager_email = Column(Text)
	
	
class LearnerMentorRankings(Base):
	__tablename__ = 'learner_mentor_rankings'
	learner = Column(Text, primary_key=True)
	mentor = Column(Text, primary_key=True)
	ranking = Column(Integer)
	
	
class MentorLearnerRankings(Base):
	__tablename__ = 'mentor_learner_rankings'
	mentor = Column(Text, primary_key=True)
	learner = Column(Text, primary_key=True)
	ranking = Column(Integer)

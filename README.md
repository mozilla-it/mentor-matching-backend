# Backend serving Mentor-Mentee-Matching
This project provides a GraphQL endpoint for updating and retrieving Mentor-Mentee matches. 
It uses a Flask, SQLAlchemy (BigQuery) and Graphene stack deployed on Google Cloud using Cloud Functions.

## Installing Requirements
Use Virtualenv and install the packages.
```
pip install -r requirements.txt
```
## Running Flask Server
Go to the root dir and run the below line in the terminal.
```
python app.py
```

## Testing GraphQL
Go to http://localhost:5000/graphql to try GraphQL. 

Below are some example queries.

### Adding or Updating a Learner
```
mutation {
  createOrUpdateLearner(email: "dummy@learner.com", 
    ts: "2999-01-01", 
    role:"dummy", 
    availability:"dummy",
    orgLevel: "dummy",
    org: "dummy",
    interest: "dummy",
    changeTrack:0,
    outsideOrg: 0,
    fullName: "dummy") {
    learner {
      email,
      timestamp,
      role
    }
    rankings {
      learner,
      mentor,
      ranking
    }
    ok
  }
}
```
### Adding or Updating a Mentor
```
mutation {
  createOrUpdateMentor(email: "dummy@mentor.com", 
    ts: "2999-01-01", 
    role:"dummy", 
    availability:"dummy",
    orgLevel: "dummy",
    org: "dummy",
    expertise: "dummy",
    outsideOrg: 0,
    fullName: "dummy") {
    mentor {
      email,
      timestamp,
      role
    }
    rankings {
      mentor,
      learner,
      ranking
    }
    ok
  }
}
```
### Get Rankings for a Learner
```
{
  findLearnerRankings(learner: "dummy@learner.com") {
        learner
        mentor
        ranking
      }
}
}
```
### Get Rankings for a Mentor
```
{
  findMentorRankings(mentor: "dummy@mentor.com") {
    id,
    mentor,
    learner,
    ranking
  }
}
```
### Get Preferences for a Learner
```
{
  findLearner(email: "dummy@learner.com") {
    id,
    email,
    timestamp,
    role,
    availability,
    org,
    interest
  }
}
```
### Get Preferences for a Mentor
```
{
  findMentor(email: "dummy@mentor.com") {
    id,
    EmailAddress,
    expertise
  }
}
```
## Data Dictionary
Below are the query field definitions.
```
ts: datetime of when user submitted request, string format "YYYY-MM-DD HH:mm:ss" in UTC
role: "Learner" if calling createOrUpdateLearner, "Mentor" if calling createOrUpdateMentor (to be removed in future version)
availability: comma-delimited string of any of the following values (change to custom granularity and convert historical data in future version)
{
00:00 - 03:00 UTC (8:00-11:00 Taiwan) (4pm-7pm US/Pacific) (1:00-4:00 CEST)
03:00 - 06:00 UTC (11:00-14:00 Taiwan) (7pm-10pm US/Pacific) (4:00-7:00 CEST)
06:00 - 09:00 UTC (14:00-17:00 Taiwan) (10pm-1am US/Pacific) (7:00-10:00 CEST)
15:00 - 18:00 UTC (23:00-2:00 Taiwan) (7am-10am US/Pacific) (16:00-19:00 CEST)
18:00 - 21:00 UTC (2:00-5:00 Taiwan) (10am-1pm US/Pacific) (19:00-22:00 CEST)
21:00 - 00:00 UTC (5:00-8:00 Taiwan) (1pm-4pm US/Pacific) (22:00-1:00 CEST)
}
orgLevel: one of the following values (remove this question from UI in future version)
{
M3
M4	
M5
M6
P2
P3
P4
P5
P6
P7
}
org: one of the following values
{
Emerging Technology
Firefox
IT
"Other Value Provided by user"
}
interest or expertise: comma-delimited string of any of the following values
{
Technical Leadership
Increasing impact on Mozilla's Mission
Getting things done at Mozilla (navigating organizational culture)
Interpersonal Communication
Time Management
Technial Skills
"Other Value Provided by user"
}
changeTrack: value between 1 and 5
outsideOrg: value between 1 and 3
```

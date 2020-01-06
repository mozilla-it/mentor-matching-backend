# Backend serving Mentor-Mentee-Matching
This project provides a GraphQL endpoing for updating and retrieving Mentor-Mentee mataches. 
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

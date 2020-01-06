from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import os

# Google Cloud config
gcp_credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
gcp_project = os.environ.get('GCP_PROJECT')
# Google BigQuery config
bigquery_dataset = 'mentoring'
bigquery_uri = f'bigquery://{gcp_project}/{bigquery_dataset}'

engine = create_engine(bigquery_uri, credentials_path=gcp_credentials)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models import User, Mentor, Learner, LearnerMentorRankings, MentorLearnerRankings
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


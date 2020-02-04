from .util import safe_cast

class Mozillian:
  """ A class to represent a person attributes """

  def __init__(self, row): # email, org_level, org, full_name, manager_email):

    self.email = str(row['Email Address']).lower()
    self.org_level = row['Organizational level (i.e. P3, M2, etc.)']
    self.track = self.org_level[0] if len(self.org_level) == 2 else ''
    self.level = safe_cast(self.org_level[1], int, 0) if len(self.org_level) == 2 else 0
    self.org = row['Organization']
    self.full_name = row['Participant full name']
    self.manager_email = str(row['Manager email']).lower()
    # add something for reporting chains including self
    self.gender = str(row['Gender']).lower()

  def get_id(self) -> str:
    """ person's unique identifier """
    return self.email

  def get_org_level(self) -> str:
    return self.org_level
        
  def get_track(self) -> str:
    return self.track
    
  def get_level(self) -> int:
    return self.level

  def get_org(self) -> str:
    return self.org
        
  def get_manager_email(self) -> str:
    return self.manager_email
    
  def get_gender(self) -> str:
    return self.gender

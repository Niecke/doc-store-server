class CurrentUser:
    def __init__(self):
        self._user = None
    
    def set_user(self, user):
        self._user = user
    
    @property
    def is_authenticated(self):
        return self._user is not None and self._user.is_authenticated()
    
    @property
    def is_anonymous(self):
        return not self.is_authenticated
    
    @property
    def id(self):
        return self._user.id if self._user else None
    
    def has_role(self, role_name):
        if not self._user:
            return False
        return any(r.name == role_name for r in self._user.roles)
    
    @property
    def roles(self):
        return self._user.roles if self._user else []
    
    @property
    def email(self):
        return self._user.email if self._user else ""

current_user = CurrentUser()

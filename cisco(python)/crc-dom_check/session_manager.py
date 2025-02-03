import requests

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        
    def get_session(self):
        return self.session
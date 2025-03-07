import paramiko
import requests
import urllib3
from requests.auth import HTTPBasicAuth
import json
import ssl
import atexit

class Login:
    def __init__(self, server, session):
        self.server = server
        self.session = session
        self.session.verify = False
        self.cookies = None
        
    def vcenter_login(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update({'Content-Type': 'application/json'})
        url = f'https://{self.server["ip"]}/rest/com/vmware/cis/session'
        response = self.session.post(url, auth=HTTPBasicAuth(self.server['id'], self.server['password']))
        if response.status_code == 200:
            self.session_token = response.json()['value']
            print(f"{self.server['ip']} Login succesful")
            return self.session_token
        else:
            print(f"{self.server['ip']} Login Failed: {response.status_code} - {response.text}")
            return None
    
    def linux(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname=self.switch['ip'],
                port=22,
                username=self.switch['id'],
                password=self.switch['password'],
                look_for_keys=False,
                allow_agent=False,
            )
            print(f"{self.server['name']} Login Successful")
            return ssh_client
        except paramiko.SSHException as e:
            print(f"{self.server['name']} Login Failed : {e}")
            return None
        
    
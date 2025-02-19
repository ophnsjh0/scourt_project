import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder

class Login:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.cookies = None
        # self.ssh_client = ssh_client

    def aci(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update({'Content-Type': 'application/json'})
        url = f'https://{self.switch["ip"]}/api/aaaLogin.json'
        login = {
            "aaaUser": {
                "attributes": {
                    "name": f"{self.switch['id']}",
                    "pwd": f"{self.switch['password']}",
                }
            }
        }
        response = self.session.post(url, json=login, verify=False)
        if response.status_code == 200:
            auth_token = json.loads(response.text)["imdata"][0]["aaaLogin"]["attributes"]["token"]
            self.cookie = {"APIC-cookie": auth_token}
            print(f"{self.switch['name']} Login Successful")
            return self.cookie
        else:
            print(f"{self.switch['name']} Login failed: {response.text}")
            print(response.status_code)
            exit()

    def ndi(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update({"Content-Type": "application/json"})
        url = f'https://{self.switch["ip"]}/login'
        login = {
            "domain" : "local",
            "userName" : f"{self.switch['id']}",
            "userPasswd" : f"{self.switch['password']}"
            
        }
        response = self.session.post(url, json=login, verify=False)
        if response.status_code == 200:
            auth_token = json.loads(response.text)["token"]
            self.cookie = {'Cookie' : f"AuthCookie={auth_token}"}
            print(f"{self.switch['name']} Login Successful")
            return self.cookie
        else:
            print(f"{self.switch['name']} Login failed: {response.text}")
            print(response.status_code)
            exit()

    def citrix(self):
        requests.packages.urllib3.disable_warnings()
        url = f'https://{self.switch["ip"]}/nitro/v1/config/login'
        login = {
            "login" :
                {
                    "username" : f"{self.switch['id']}",
                    "password" : f"{self.switch['password']}",
                    "timeout" : "60"
                }
        }
        response = self.session.post(url, json=login)
        if response.status_code == 201 or response.status_code == 200:
            sessionid = json.loads(response.text)['sessionid']
            self.cookies = {'Cookie' : f"NITRO_AUTH_TOKEN={sessionid}"}
            print(f"{self.switch['name']} Login Successful")
            return self.cookies
        else:
            print(f"{self.switch['name']} Login failed: {response.text}")
            print(response.status_code)
            exit()
            
    def cisco(self):
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
            print(f"{self.switch['name']} Login Successful")
            return ssh_client
        except paramiko.SSHException as e:
            print(f"{self.switch['name']} Login Failed: {e}")
            return None

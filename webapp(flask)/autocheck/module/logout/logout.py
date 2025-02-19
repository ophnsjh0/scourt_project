import requests
import json
from json.decoder import JSONDecoder

class Logout:
    def __init__(self, switch, session):
        self.switch = switch 
        self.session = session
        self.session.verify = False
        self.cookies = None

    def citris(self):
        requests.packages.urllib3.disable_warnings()
        url = f'https://{self.switch["ip"]}/nitro/v1/config/logout'
        data = {'logout' : {}}
        response = self.session.post(url, json=data)
        if response.status_code == 201:
            print(f"{self.switch['name']} Logout Successful")
        else:
            print(f"{self.switch['name']} Logout Failed: {response.text}")
            print(response.status_code)
            exit(1)

    def aci(self):
        requests.packages.urllib3.disable_warnings()
        url = f'https://{self.switch["ip"]}/api/aaaLogout.json'
        logout = {
            "aaaUser" : {
                "attributes" : {
                    "name" : f"{self.switch['id']}"
                }
            }
        }
        response = self.session.post(url, json=logout)
        if response.status_code == 200:
            print(f"{self.switch['name']} Logout Successful")
        else:
            print(f"{self.switch['name']} Logout Failed: {response.text}")
            print(response.status_code)
            exit(1)

    def cisco(self, ssh_client):
        if ssh_client:
            ssh_client.close()
            print(f"{self.switch['name']} Logout Successful")
        else:
            print(f"{self.switch['name']} Logout Failed: Not ssh_client")

    # # aci와 동일
    # def ndi(self)
    #     requests.packages.urllib3.disable_warnings()
    #     url = f'https://{self.switch["ip"]}/api/aaaLogout.json'
    #     logout = {
    #         "aaaUser" : {
    #             "attributes" : {
    #                 "name" : f"{self.switch['id']}"
    #             }
    #         }
    #     }
    #     response = self.session.post(url, json=logout)
    #     if response.status_code == 200:
    #         print(f"{self.switch['name']} Logout Successful")
    #     else:
    #         print(f"{self.switch['name']} Logout Failed: {response.text}")
    #         print(response.status_code)
    #         exit(1)

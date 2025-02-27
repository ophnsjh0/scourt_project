import requests
import json
import time
from json.decoder import JSONDecoder

class AciParam:
    def __init__(self, equipment, session, token):
        self.equipment = equipment
        self.session = session
        self.token = token
        self.session.verify = False
        self.nodes = ["1101", "1102", "1201", "1202", "1301", "1302"]
        self.headers = {"Content-Type": "application/json"}

    def l3out(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(self.token)
        url = f'https://{self.equipment["ip"]}/api/node/class/l3extOut.json?rsp-subtree=full&rsp-subtree-class=ipRouteP'
        response = self.session.get(url=url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()['imdata']
            return result
        else:
            print(f"{self.equipment['name']} get l3out : Failed")
            exit()

    def bd_to_l3out(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(self.token)
        url = f'https://{self.equipment["ip"]}/api/node/class/fvBD.json?rsp-subtree=full&rsp-subtree-class=fvRsBDToOut'
        response = self.session.get(url=url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()["imdata"]
            return result
        else:
            print(f"{self.equipment['name']} get bd_iinfo : Failed")
            exit()

    def bd_to_vrf(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(self.token)
        url = f'https://{self.equipment["ip"]}/api/node/class/fvBD.json?rsp-subtree=full&rsp-subtree-class=fvRsCtx&rsp-subtree-class=fvSubnet'
        response = self.session.get(url=url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()["imdata"]
            return result
        else:
            print(f"{self.equipment['name']} get vrf_info : Failed")
            exit()

    def vrf(self):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(self.token)
        url = f'https://{self.equipment["ip"]}/api/node/class/fvCtx.json'
        response = self.session.get(url=url, headers=self.headers)
        if response.status_code == 200:
            result = response.json()["imdata"]
            return result
        else:
            print(f"{self.equipment['name']} get vrf_info : Failed")
            exit()

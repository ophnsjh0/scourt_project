import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder
from datetime import datetime


class GetTemp:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        temp_data = []
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/mo/topology/pod-1/node-{node}/sys/ch/supslot-1/sup/sensor-1/CDeqptTemp5min.json'
            response = self.session.get(url)
            if response.status_code == 200:
                temp = response.json()["imdata"][0]['eqptTemp5min']['attributes']
                temp_data.append(temp)
                print(f"{node} get Temperature : ok")
            else:
                print(f"{node} get Temperature : Failed")
                exit()
        return temp_data

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show env temperature | inc Temperature Value"
            )
            time.sleep(1)
            temp_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get Temperature : OK")
            return temp_data
        else:
            print(f"{self.switch['name']} Get Temperature : Failed")
            return None

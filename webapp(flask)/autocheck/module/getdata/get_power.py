import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder
from datetime import datetime


class GetPower:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/api/node/class/eqptPsu.json'
        response = self.session.get(url)
        if response.status_code == 200:
            power_data = response.json()["imdata"]
            print(f"ACI get Power : ok")
        else:
            print(f"ACI get Power : Failed")
            exit()
        return power_data

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show env power"
            )
            time.sleep(1)
            power_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get Power : OK")
            return power_data
        else:
            print(f"{self.switch['name']} Get Power : Failed")
            return None

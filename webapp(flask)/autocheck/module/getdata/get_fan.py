import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder
from datetime import datetime


class GetFan:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/api/node/class/eqptFt.json'
        response = self.session.get(url)
        if response.status_code == 200:
            fan_data = response.json()["imdata"]
            print(f"ACI get Fan : ok")
        else:
            print(f"ACI get Fan : Failed")
            exit()
        return fan_data

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show env fan"
            )
            time.sleep(1)
            fan_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get Fan : OK")
            return fan_data
        else:
            print(f"{self.switch['name']} Get Fan : Failed")
            return None

    # def citrix(self, token):
    #     requests.packages.urllib3.disable_warnings()
    #     self.session.headers.update(token)
    #     url = f'https://{self.switch["ip"]}/nitro/v1/stat/system'
    #     response = self.session.get(url)
    #     if response.status_code == 200:
    #         cpu_data = response.json()["system"]
    #         print(f"{self.switch['name']} Get CPU : OK")
    #         return cpu_data
    #     else:
    #         print(f"{self.switch['name']} Get CPU : Failed")
    #         return None

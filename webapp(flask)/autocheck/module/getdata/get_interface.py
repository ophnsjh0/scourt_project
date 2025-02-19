import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder


class GetInterface:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        interface_data = []
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/class/topology/pod-1/node-{node}/ethpmPhysIf.json'
            response = self.session.get(url)
            if response.status_code == 200:
                interfaces = response.json()["imdata"]
                print(f"{node} get interface : ok")
                interface_data.append(interfaces)
            else:
                print(f"{node} get interface : Failed")
                exit()
        return interface_data

    def citrix(self, token):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/stat/interface'
        response = self.session.get(url)
        if response.status_code == 200:
            interface_data = response.json()["Interface"]
            print(f"{self.switch['name']} Get interface : OK")
            return interface_data
        else:
            print(f"{self.switch['name']} Get interface : Failed")
            return None

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show interface status"
            )
            time.sleep(1)
            interface_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get interface : OK")
            ssh_client.close()
            return interface_data
        else:
            print(f"{self.switch['name']} Get interface : Failed")
            return None

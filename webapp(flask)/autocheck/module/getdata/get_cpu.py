import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder

class GetCpu:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        cpu_data = []
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/mo/topology/pod-1/node-{node}/sys/procsys/HDprocSysCPU5min-0.json'
            response = self.session.get(url)
            if response.status_code == 200:
                cpu = response.json()['imdata']
                print(f"{node} get cpu : ok")
                cpu_data.append(cpu)
            else:
                print(f"{node} get cpu : Failed")
                exit()
        return cpu_data

    def citrix(self, token):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/stat/system'
        response = self.session.get(url)
        if response.status_code == 200:
            cpu_data = response.json()['system']
            print(f"{self.switch['name']} Get CPU : OK")
            return cpu_data
        else:
            print(f"{self.switch['name']} Get CPU : Failed")
            return None

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command("show process cpu | include CPU")
            time.sleep(1)
            cpu_data = stdout.read().decode('utf-8')
            print(f"{self.switch['name']} Get CPU : OK")
            return cpu_data
        else:
            print(f"{self.switch['name']} Get CPU : Failed")
            return None

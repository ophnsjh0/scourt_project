import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder


class GetMem:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        mem_data = []
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/mo/topology/pod-1/node-{node}/sys/procsys/HDprocSysMem5min-0.json'
            response = self.session.get(url)
            if response.status_code == 200:
                mem = response.json()["imdata"]
                print(f"{node} get cpu : ok")
                mem_data.append(mem)
            else:
                print(f"{node} get cpu : Failed")
                exit()
        return mem_data

    def citrix(self, token):
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/stat/ns'
        response = self.session.get(url)
        if response.status_code == 200:
            cpu_data = response.json()["ns"]
            print(f"{self.switch['name']} Get MEM : OK")
            return cpu_data
        else:
            print(f"{self.switch['name']} Get MEM : Failed")
            return None

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show memory summury | inc Processor"
            )
            time.sleep(1)
            cpu_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get MEM : OK")
            return cpu_data
        else:
            print(f"{self.switch['name']} Get MEM : Failed")
            return None

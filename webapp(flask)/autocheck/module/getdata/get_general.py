import paramiko
import requests
import json
import time
from json.decoder import JSONDecoder
from datetime import datetime


class GetGeneral:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        general_data = []
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/mo/topology/pod-1/node-{node}/sys/ch/supslot-1/sup.json'
            response = self.session.get(url)
            if response.status_code == 200:
                general = response.json()["imdata"][0]['eqptSupC']['attributes']
                print(f"{node} get Genaral : ok")
            else:
                print(f"{node} get Genaral : Failed")
                exit()
            url2 = f'https://{self.switch["ip"]}/api/{node}/class/firmwareRunning.json'
            response2 = self.session.get(url2)
            if response2.status_code == 200:
                version = response2.json()["imdata"][0]['firmwareRunning']['attributes']
                print(f"{node} get Genaral : ok")
            else:
                print(f"{node} get Genaral : Failed")
                exit()
            sum_data = general | version
            general_data.append(sum_data)

        return general_data

    def citrix(self, token):
        general_data = []
        uri_info = ['nsversion', 'nshardware', 'nsconfig', 'nshostname']
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        for uri in uri_info:
            url = f'https://{self.switch["ip"]}/nitro/v1/config/{uri}'
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()[f"{uri}"]
                general_data.append(data)
                print(f"{self.switch['name']} Get {uri} : OK")
            else:
                print(f"{self.switch['name']} Get General : Failed")
                return None

        return general_data

    def cisco(self, ssh_client):
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(
                "show version"
            )
            time.sleep(1)
            cpu_data = stdout.read().decode("utf-8")
            print(f"{self.switch['name']} Get General : OK")
            return cpu_data
        else:
            print(f"{self.switch['name']} Get General : Failed")
            return None

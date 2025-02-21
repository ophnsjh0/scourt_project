import requests
import json
from json.decoder import JSONDecoder


class GetSlb:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False

    def vserver(self, token):
        cpu_data = []
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/config/lbvserver'
        response = self.session.get(url)
        if response.status_code == 200:
            vserver_data = response.json()["lbvserver"]
            print(f"{self.switch} get Vserver : ok")
            return vserver_data
        else:
            print(f"{self.switch} get Vserver : Failed")
            return None

    def service(self, token):
        service_data = []
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/config/service'
        response = self.session.get(url)
        if response.status_code == 200:
            service = response.json()["service"]
            print(f"{self.switch['name']} Get Service : OK")
            return service
        else:
            print(f"{self.switch['name']} Get Service : Failed")
            return None

    def service_binding(self, token, vserver_data):
        service_binding_data = []
        for vserver in vserver_data:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/nitro/v1/config/lbvserver_binding/{vserver['name']}'
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                if 'lbvserver_service_binding' in result['lbvserver_binding'][0]:
                    service = result['lbvserver_binding'][0]['lbvserver_service_binding']
                    service_binding_data.append(service)
                else:
                    print(result)
            else:
                return None
        return service_binding_data

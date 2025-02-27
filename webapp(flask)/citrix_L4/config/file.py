import requests
import json
from json.decoder import JSONDecoder

def save_to_file(l4_info, vservers):
    file = open(f'{l4_info['name']}.csv', 'w', encoding='cp949')
    file.write("Vserver, VIP, VPort, Method, Protocol, State, Service, SIP, SPORT, Protocol, State\n" )
    for vserver in vservers:
        url = f"https://{l4_info['ip']}/nitro/v1/config/lbvserver_binding/{vserver['name']}"
        headers = {"Content-Type": "application/json", "X-NITRO-USER":f"{l4_info['id']}", "X-NITRO-PASS":f"{l4_info['password']}" }
        response = requests.get(url, headers=headers, verify=False)
        result = response.json()
        lbvserver = result['lbvserver_binding']
        service = lbvserver[0]
        print(service)
        if 'lbvserver_service_binding' in service:
            service_binding = service['lbvserver_service_binding']
            for service in service_binding:
                file.write(
                    f'{vserver["name"]}, {vserver["vip"]}, {vserver["vport"]}, {vserver["lbmethod"]}, {vserver["protocol"]}, {vserver["state"]}, {vserver["servicename"]}, {vserver["ipv46"]}, {vserver["port"]}, {vserver["servicetype"]}, {vserver["curstate"]}\n'
                )
        else:
            file.write(
                    f'{vserver["name"]}, {vserver["vip"]}, {vserver["vport"]}, {vserver["lbmethod"]}, {vserver["protocol"]}, {vserver["state"]}, -, -, -, -, -\n'
                )
            
    file.close()
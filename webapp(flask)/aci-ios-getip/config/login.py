import paramiko
import requests
import json
import time


def aci_Login(center, session):
    requests.packages.urllib3.disable_warnings()
    session.headers.update({"Content-Type": "application/json"})
    url = f'https://{center["ip"]/api/aaaLogin.json}'
    login = {
        "aaaUser": {
            "attributes": {
                "name": f"{center['id']}",
                "pwd": f"{center['password']}",
            }
        }
    }
    response = session.post(url, json=login, verify=False)
    if response.status_code == 200:
        auth_token = json.loads(response.text)["imdata"][0]["aaaLogin"]["attributes"][
            "token"
        ]
        cookie = {"APIC-cookie": auth_token}
        print(f"{center['ip']} Login Successful")
        return cookie
    else:
        print(f"{center['ip']} Login failed: {response.text}")
        print(response.status_code)
        exit()
        
def l2_Login(center):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(1, retries + 1):
        try:
            ssh_client.connect(
                hostname=center['ip'],
                port=22,
                username=center['id'],
                password=center['password'],
                look_for_keys=False,
                allow_agent=False,
            )
            print(f"{center['ip']} Login Successful")
            return ssh_client
        except paramiko.SSHException as e:
            print(f"{center['name']} Login Failed: {e}")
            return None


import requests
import json

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
        auth_token = json.loads(response.text)["imdata"][0]["aaaLogin"]["attributes"]["token"]
        cookie = {"APIC-cookie": auth_token}
        return cookie
    else:
        print("Login failed")
        print(response.status_code)
        exit()


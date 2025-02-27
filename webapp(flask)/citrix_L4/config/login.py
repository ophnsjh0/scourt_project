
import requests

login = {
    "login": {
        "username": "nsroot",
        "password": "nsroot",
        "timeout": "60",
    }
}

def nitro_login():
    requests.packages.urllib3.disable_warnings()
    url = 'https://10.10.10.10/nitro/v1/config/login'
    headers = { 'Content-Type' : 'application/json' }
    response = requests.post(url, json=login, headers=headers, verify=False)
    result = response.json()
    result2 = response.headers
    print(result)
    token = result['sessionid']
    print(token)
    return token

nitro_login()


import requests
import json
from json.decoder import JSONDecoder
from cryptography.fernet import Fernet
from session_manager import SessionManager
from prettytable import PrettyTable
from aciparam import AciParam
from param_parser import ParamParser
from export_file import File


def load_key():
    return open("secret.key", "rb").read()


def load_and_decrypt_data(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data).decode()

    data_list = json.loads(decrypted_data)

    return data_list


def login_aci(aci, session):
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    session.headers.update({"Content-Type": "application/json"})
    url = f'https://{aci["ip"]/api/aaaLogin.json}'
    login = {
        "aaaUser": {
            "attributes": {
                "name": f"{aci['id']}",
                "pwd": f"{aci['password']}",
            }
        }
    }
    response = session.post(url, json=login)
    if response.status_code == 200:
        auth_token = json.loads(response.text)["imdata"][0]["aaaLogin"]["attributes"]["token"]
        cookie = {"APIC-cookie": auth_token}
        print(f"{aci['ip']} Login Successful")
        return cookie
    else:
        print(f"{aci['ip']} Login failed: {response.text}")
        print(response.status_code)
        exit()
        
if __name__ == "__main__":
    devices = load_and_decrypt_data("encrypted_list.bin")
    session_manager = SessionManager()
    session = session_manager.get_session()
    for device in devices:
        cookie = login_aci(device, session)
        # 수집
        aci = AciParam(device, session, cookie)
        l3out = aci.l3out()
        bd_to_l3out = aci.bd_to_l3out()
        bd_to_vrf = aci.bd_to_vrf()
        vrf = aci.vrf()
        # 가공
        parser = ParamParser(l3out, bd_to_l3out, vrf, bd_to_vrf)
        l3out_data = parser.aci_l3out_parser()
        vrf_data = parser.aci_vrf_parser()
        bd_data = parser.aci_bd_parser()
        # 출력
        file = File()
        file.aci_l3out(l3out_data)
        file.aci_vrf(vrf_data)
        file.aci_bd(bd_data)
        

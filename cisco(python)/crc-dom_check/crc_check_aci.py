import requests
import json
from json.decoder import JSONDecoder
from cryptography.fernet import Fernet
from session_manager import SessionManager
from prettytable import PrettyTable

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
    session.headers.update({'Content-Type': 'application/json'})
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
        auth_token = json.loads(response.text)['imdata'][0]['aaaLogin']['attributes']['token']
        cookie = {'APIC-cookie' : auth_token}
        print(f"{aci['ip']} Login Successful")
        return cookie
    else:
        print(f"{aci['ip']} Login failed: {response.text}")
        print(response.status_code)
        exit()

def crc_aci_all(aci, cookie, session):
    output = PrettyTable()
    output.field_names = [
        "node",
        "interface",
        "crc",
        "drop",
        "pkts",
        "pkts1024",
        "pkts512",
        "pkts256",
        "pkts128",
        "pkts64",
    ]
    session.headers.update(cookie)
    url = f'https://{aci['ip']}/api/node/class/rmonEtherStats.json'
    response = session.get(url)
    if response.status_code == 200:
        interfaces = response.json()['imdata']
        for phy in interfaces:
            if 'phys' in phy['rmonEtherStats']['attributes']['dn']:
                node = phy['rmonEtherStats']['attributes']['dn'][phy['rmonEtherStats']['attributes']['dn'].index('/node-') + 6: phy['rmonEtherStats']['attributes']['dn'].index('/sys')]
                phyif = phy['rmonEtherStats']['attributes']['dn'][phy['rmonEtherStats']['attributes']['dn'].index('phys-[') + 6: phy['rmonEtherStats']['attributes']['dn'].index(']/dbgEtherStats')]
                crc = phy['rmonEtherStats']['attributes']['cRCAlignErrors']
                drop = phy['rmonEtherStats']['attributes']['dropEvents']
                pkts = phy['rmonEtherStats']['attributes']['pkts']
                pkts1024 = phy['rmonEtherStats']['attributes']['pkts1024to1518Octets']
                pkts512 = phy['rmonEtherStats']['attributes']['pkt512to1023Octets']
                pkts256 = phy['rmonEtherStats']['attributes']['pkts256to511Octets']
                pkts128 = phy['rmonEtherStats']['attributes']['pkts128to255Octets']
                pkts64 = phy['rmonEtherStats']['attributes']['pkts64to127Octets']
                output.add_row(
                    [node, phyif, crc, drop, pkts, pkts1024, pkts512, pkts256, pkts128, pkts64,]
                )
    else:
        print(f"get : Failed")
        exit()
        
    print(output)
    
def crc_aci(aci, cookie, session):
    output = PrettyTable()
    output.field_names = [
        "node",
        "interface",
        "crc",
        "drop",
        "pkts",
        "pkts1024",
        "pkts512",
        "pkts256",
        "pkts128",
        "pkts64",
    ]
    session.headers.update(cookie)
    # url = f"https://{aci['ip']}/api/node/class/rmonEtherStats.json?query-target-filter=not(wcard(rmonEtherStats.cRCAlignErrors,'0'))"
    url = f"https://{aci['ip']}/api/node/class/rmonEtherStats.json?query-target-filter=gt(rmonEtherStats.cRCAlignErrors,'0')"
    response = session.get(url)
    if response.status_code == 200:
        interfaces = response.json()['imdata']
        for phy in interfaces:
            if 'phys' in phy['rmonEtherStats']['attributes']['dn']:
                node = phy['rmonEtherStats']['attributes']['dn'][phy['rmonEtherStats']['attributes']['dn'].index('/node-') + 6: phy['rmonEtherStats']['attributes']['dn'].index('/sys')]
                phyif = phy['rmonEtherStats']['attributes']['dn'][phy['rmonEtherStats']['attributes']['dn'].index('phys-[') + 6: phy['rmonEtherStats']['attributes']['dn'].index(']/dbgEtherStats')]
                crc = phy['rmonEtherStats']['attributes']['cRCAlignErrors']
                drop = phy['rmonEtherStats']['attributes']['dropEvents']
                pkts = phy['rmonEtherStats']['attributes']['pkts']
                pkts1024 = phy['rmonEtherStats']['attributes']['pkts1024to1518Octets']
                pkts512 = phy['rmonEtherStats']['attributes']['pkt512to1023Octets']
                pkts256 = phy['rmonEtherStats']['attributes']['pkts256to511Octets']
                pkts128 = phy['rmonEtherStats']['attributes']['pkts128to255Octets']
                pkts64 = phy['rmonEtherStats']['attributes']['pkts64to127Octets']
                output.add_row(
                    [node, phyif, crc, drop, pkts, pkts1024, pkts512, pkts256, pkts128, pkts64,]
                )
    else:
        print(f"get : Failed")
        exit()
        
    print(output)
    
if __name__ == "__main__":
    devices = load_and_decrypt_data("encrypted_list_aci.bin")
    session_manager = SessionManager()
    session = session_manager.get_session()
    for device in devices:
        cookie = login_aci(device, session)
        # crc_aci_all(device, cookie, session)
        crc_aci(device, cookie, session)
    
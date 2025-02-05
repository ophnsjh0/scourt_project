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
        auth_token = json.loads(response.text)["imdata"][0]["aaaLogin"]["attributes"][
            "token"
        ]
        cookie = {"APIC-cookie": auth_token}
        print(f"{aci['ip']} Login Successful")
        return cookie
    else:
        print(f"{aci['ip']} Login failed: {response.text}")
        print(response.status_code)
        exit()

def dom_aci_all(aci, cookie, session):
    print(f"{aci['name']} Pod에 점검할 Node를 입력하세요(Enter(미입력)시 전체점검)")
    node_info = input("점검NODE : ")
    output = PrettyTable()
    output.field_names = ['node', 'interface', 'RX_Power', 'TX_Power', '전류', '전압', '온도', '상태']
    session.hearders.update(cookie)
    url = f'https://{aci["ip"]}/api/node/class/ethpmDOMStats.json?rsp-subtree=children'
    response = session.get(url)
    if response.status_code == 200:
        doms = response.json()['imdata']
        for dom in doms:
            dom_state = dom["ethpmDOMStats"]['attributes']['dn']
            dom_current = dom["ethpmDOMStats"][0]["ethpmDOMCurrentStats"]["attributes"]
            dom_rx = dom["ethpmDOMStats"][1]["ethpmDOMRxPwrStats"]["attributes"]
            dom_tx = dom["ethpmDOMStats"][3]["ethpmDOMTxPwrStats"]["attributes"]
            dom_volt = dom["ethpmDOMStats"][4]["ethpmDOMVoltStats"]["attributes"]
            dom_temp = dom["ethpmDOMStats"][2]["ethpmDOMTempStats"]["attributes"]

            if node_info in dom_state[dom_state.index('/node-') + 6: dom_state.index('/sys') ]:
                if dom_current['value'] == '0.000000' or dom_rx['value'] == '-40.000000' or dom_current['value'] == '0.002000':
                    state = "미사용"
                elif float(dom_current['value']) >= float(dom_current['hiWarn']) or float(dom_current['value']) <= float(dom_current['loWarn']):
                    state = "Current_Err"
                elif float(dom_rx['value']) >= float(dom_rx['hiWarn']) or float(dom_rx['value']) <= float(dom_current['loWarn']):
                    state = "RX_Power_Err"
                elif float(dom_tx["value"]) >= float(dom_tx["hiWarn"]) or float(dom_tx["value"]) <= float(dom_current["loWarn"]):
                    state = "TX_Power_Err"
                elif float(dom_volt["value"]) >= float(dom_volt["hiWarn"]) or float(dom_volt["value"]) <= float(dom_volt["loWarn"]):
                    state = "Voltage_Err"
                elif float(dom_temp["value"]) >= float(dom_temp["hiWarn"]) or float(dom_temp["value"]) <= float(dom_current["loWarn"]):
                    state = "Temp_Err"
                else:
                    state = "정상"
                node = dom_state[dom_state.index('/node-') + 6: dom_state.index('/sys')]
                phyif = dom_state[dom_state.index('phys-[') + 6: dom_state.index(']/phys')]
                rx = dom_rx['value']
                tx = dom_tx["value"]
                current = dom_current["value"]
                volt = dom_volt["value"]
                temp = dom_temp["value"]
                output.add_row([node, phyif, rx, tx, current, volt, temp, state])
    else:
        print(f"get : Failed")
        exit()
        
    print(output)

def dom_aci_occur(aci, cookie, session):
    output = PrettyTable()
    output.field_names = [
        "node",
        "interface",
        "RX_Power",
        "TX_Power",
        "전류",
        "전압",
        "온도",
        "상태",
    ]
    session.hearders.update(cookie)
    url = f'https://{aci["ip"]}/api/node/class/ethpmDOMStats.json?rsp-subtree=children'
    response = session.get(url)
    if response.status_code == 200:
        doms = response.json()["imdata"]
        for dom in doms:
            dom_state = dom["ethpmDOMStats"]["attributes"]["dn"]
            dom_current = dom["ethpmDOMStats"][0]["ethpmDOMCurrentStats"]["attributes"]
            dom_rx = dom["ethpmDOMStats"][1]["ethpmDOMRxPwrStats"]["attributes"]
            dom_tx = dom["ethpmDOMStats"][3]["ethpmDOMTxPwrStats"]["attributes"]
            dom_volt = dom["ethpmDOMStats"][4]["ethpmDOMVoltStats"]["attributes"]
            dom_temp = dom["ethpmDOMStats"][2]["ethpmDOMTempStats"]["attributes"]

            if (node_info in dom_state[dom_state.index("/node-") + 6 : dom_state.index("/sys")]):
                if (dom_current["value"] == "0.000000" or dom_rx["value"] == "-40.000000" or dom_current["value"] == "0.002000"):
                    state = "미사용"
                elif float(dom_current["value"]) >= float(dom_current["hiWarn"]) or float(dom_current["value"]) <= float(dom_current["loWarn"]):
                    state = "Current_Err"
                elif float(dom_rx["value"]) >= float(dom_rx["hiWarn"]) or float(dom_rx["value"]) <= float(dom_current["loWarn"]):
                    state = "RX_Power_Err"
                elif float(dom_tx["value"]) >= float(dom_tx["hiWarn"]) or float(dom_tx["value"]) <= float(dom_current["loWarn"]):
                    state = "TX_Power_Err"
                elif float(dom_volt["value"]) >= float(dom_volt["hiWarn"]) or float(dom_volt["value"]) <= float(dom_volt["loWarn"]):
                    state = "Voltage_Err"
                elif float(dom_temp["value"]) >= float(dom_temp["hiWarn"]) or float(dom_temp["value"]) <= float(dom_current["loWarn"]):
                    state = "Temp_Err"
                else:
                    state = "정상"
                    
                if state != "정상" and state != "미사용":
                    node = dom_state[dom_state.index("/node-") + 6 : dom_state.index("/sys")]
                    phyif = dom_state[dom_state.index("phys-[") + 6 : dom_state.index("]/phys")]
                    rx = dom_rx["value"]
                    tx = dom_tx["value"]
                    current = dom_current["value"]
                    volt = dom_volt["value"]
                    temp = dom_temp["value"]
                    output.add_row([node, phyif, rx, tx, current, volt, temp, state])
    else:
        print(f"get : Failed")
        exit()

    print(output)

if __main__ == "__main__":
    devices = load_and_decrypt_data("encrypted_list_aci.bin")
    session_manager = SessionManager()
    session = session_manager.get_session()
    for device in devices:
        cookie = login_aci(device, session)
        # dom_aci_all(device, cookie, session)
        dom_aci_occur(device, cookie, session)
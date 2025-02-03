import requests
import os
import sys
import getopt
import json
from prettytable import PrettyTable
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url = os.environ['ACI_URL']
username = os.environ['ACI_USERNAME']
password = os.environ['ACI_PASSWORD']
ssl_verify = False if 'ACI_SSLVERIFY' in os.environ and os.environ['ACI_SSLVERIFY'] == "False" else True
headers = {"Content-Type": "application/json"}

def auth():
    payload = f'''{{"aaaUser": {{"attributes": {{ "name": "{ username }", "pwd": "{ password }" }} }} }}'''
    response = requests.post(f'{base_url}/api/aaaLogin.json', headers=headers, data=payload, verify=ssl_verify)
    if response.status_code == 200:
        headers["Cookie"] = f'APIC-cookie={response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]}'
    else:
        raise Exception("ACI auth failed.") 

def get(page_size=100, filters={}):
    imdata = []
    page = 0
    while True:
        url = f"{base_url}/api/node/class/l1PhysIf.json?page-size={page_size}&page={page}&order-by=l1PhysIf.dn|asc"
        if 'descr_only' in filters:
            url += '&query-target-filter=ne(l1PhysIf.descr,"")'
        res = requests.get(url=url, headers=headers, verify=ssl_verify)
        try:
            res.json()["imdata"][0]
            for item in res.json()["imdata"]:
                imdata.append(item)
        except:
            break
        page += 1
    return json.dumps({"imdata": imdata})

def printInterfacesTable(imdata):
    output = PrettyTable()
    output.field_names = ["pod", "node", "interface", "adminSt" ,"mtu", "mode", "descr"]
    output.align = "l"
    for item in json.loads(imdata)["imdata"]:
        attr = item["l1PhysIf"]["attributes"]
        output.add_row(
            [
                attr["dn"].split('/')[1].split('-')[1],     # pod
                attr["dn"].split('/')[2].split('-')[1],     # node
                attr["dn"].split('-')[3][1:-1],             # interface
                attr["adminSt"],
                attr["mtu"],
                attr["mode"],
                attr["descr"]
            ]
        )
    print(output)

if __name__ == "__main__":
    argv = sys.argv[1:]
    page_size = 100
    filters = {}
    options, args = getopt.getopt(argv, "p:ds:", ["page-size", "descr-only", "operst"])
    for name, value in options:
        if name in ['-d', '--descr-only']:
            filters['descr_only'] = True
        if name in ['-p', '--page-size']:
            page_size = value
    auth() 
    imdata = get(page_size=page_size, filters=filters)
    printInterfacesTable(imdata)
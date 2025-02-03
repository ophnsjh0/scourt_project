import requests
import os
import sys
import argparse
import json
import re
import warnings
import pandas as pd
from prettytable import PrettyTable

from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url = os.environ['ACI_URL']
username = os.environ['ACI_USERNAME']
password = os.environ['ACI_PASSWORD']
ssl_verify = False if 'ACI_SSLVERIFY' in os.environ and os.environ['ACI_SSLVERIFY'] == "False" else True
headers = {"Content-Type": "application/json"}

def auth():
    """
    get login token and etc.
    """
    payload = f'{{"aaaUser": {{ "attributes": {{ "name": "{ username }", "pwd": "{ password }" }} }} }}'
    response = requests.post(f'{base_url}/api/aaaLogin.json', headers=headers, data=payload, verify=ssl_verify)
    if response.status_code == 200:
        headers['Cookie'] = f"APIC-cookie={response.json()['imdata'][0]['aaaLogin']['attributes']['token']}"
    else:
        raise Exception("ACI auth failed.")
    return response.json()['imdata'][0]['aaaLogin']['attributes']

def checkAPICVer(version):
    """ check ACI version, then stop program when using limited ACI version """
    if version.startswith('6') or version.startswith('5.3') or version == '5.2(8e)':
        pass
    else:
        print(f'APIC {version} is not supported.')
        sys.exit(1)

def get_fvCEp_fvIp(page_size=1000):
    """
    get all of endpoints(fvCEp) and IP addresses(fvIp)
    """
    imdata = []
    page = 0
    while True:
        url = f'{base_url}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvIp&page-size={page_size}&page={page}&order-by=fvCEp.dn'
        res = requests.get(url=url, headers=headers, verify=ssl_verify)
        try:
            res.json()['imdata'][0]
            for item in res.json()['imdata']:
                imdata.append(item)
        except:
            break
        page += 1
    return { "imdata": imdata }

def get_infraPortSummary(page_size=1000):
    """
    get interface configuration
    """
    imdata = []
    page = 0
    while True:
        url = f'{base_url}/api/node/class/infraPortSummary.json?page-size={page_size}&page={page}&order-by=infraPortSummary.dn'
        res = requests.get(url=url, headers=headers, verify=ssl_verify)
        try:
            res.json()['imdata'][0]
            for item in res.json()['imdata']:
                imdata.append(item)
        except:
            break
        page += 1
    return { "imdata": imdata }

def flatten(imdata):
    """
    merge the relevant endpoint and IP address into one row.
    """
    output = []
    for item in imdata['imdata']:
        ep = item['fvCEp']['attributes']

        # INFO: infra, mgmt tenants are ignored.
        if '/tn-infra/' in ep['dn'] or '/tn-mgmt/' in ep['dn']:
            continue
        
        # INFO: An endpoint can have multiple IP addresses or nothing.
        if "children" in item['fvCEp']:
            for child in item['fvCEp']['children']:
                output.append(
                    {
                        "host":         ep['contName'],
                        "mac":          ep['mac'], 
                        "addr":         child['fvIp']['attributes']['addr'],
                        "fabricPathDn": ep['fabricPathDn'],
                        "ep":           ep['dn'],
                        "vrf":          ep['vrfDn']
                    }
                )
        else:
            output.append(
                {
                    "host":         ep['contName'],
                    "mac":          ep['mac'], 
                    "addr":         "",
                    "fabricPathDn": ep['fabricPathDn'],
                    "ep":           ep['dn'],
                    "vrf":          ep['vrfDn']
                }
            )
    return { "imdata": output }

def mapping(endpoints, portSumm):
    """
    merge the relevant endpoint and interfaces into one row.
    """
    output = []
    for ep in endpoints['imdata']:
        tn       = ep['ep'].split('/')[1][3:]
        epg      = ""
        esg      = ""
        vrf      = ""
        descr    = ""
        pcIf     = ""  
        physIf   = ""
        node     = ""
        LDevInst = ""

        # INFO: Retrieve description from a dictionary using fabricPathDn
        if ep['fabricPathDn'] != "":
            ep_paths  = ep['fabricPathDn'][ep['fabricPathDn'].index('/paths-') + 7 : ep['fabricPathDn'].index('/pathep-')]
            ep_pathep = ep['fabricPathDn'][ep['fabricPathDn'].index('/pathep-[') + 9 : -1]
            node      = ep_paths

            for item in portSumm['imdata']:
                port = item['infraPortSummary']['attributes']

                if pcIf == '' and port['pcPortDn'] != '':
                    src = port['pcPortDn']
                    if '/protpaths-' in src:
                        chk_nodes = src[src.index('/protpaths-') + 11 : src.index('/pathep-')].split('-')
                        chk_path  = src[src.index('/pathep-[') + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr  = port['description']
                            physIf = port['portDn'][port['portDn'].index('/pathep-[') + 9 : -1]
                            pcIf   = ep_pathep
                    elif '/paths-' in src:
                        chk_nodes = src[src.index('/paths-') + 7 : src.index('/pathep-')]
                        chk_path  = src[src.index('/pathep-[') + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr  = port['description']
                            physIf = port['portDn'][port['portDn'].index('/pathep-[') + 9 : -1]
                            pcIf   = ep_pathep
                    else:
                        raise Exception(f'{src}')
                
                elif physIf == '' and port['portDn'] != '':
                    src = port['portDn']
                    if '/paths-' in src:
                        chk_nodes = src[src.index('/paths-') + 7 : src.index('/pathep-')]
                        chk_path  = src[src.index('/pathep-[') + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr  = port['description']
                            physIf = chk_path
                    else:
                        raise Exception(f'{src}')        

        try:
            vrf = ep['vrf'][ep['vrf'].index('/ctx-') + 5: ]
        except ValueError:
            # warnings.warn(f"{ep['ep']} has no vrfDn.")
            pass

        if re.search('/epg-', ep['ep']):
            epg = ep['ep'][ep['ep'].index('/epg-') + 5 : ep['ep'].index('/cep-')]
        elif re.search('/esg-', ep['ep']):
            esg = ep['ep'][ep['ep'].index('/esg-') + 5 : ep['ep'].index('/cep-')]
        elif re.search('/ctx-', ep['ep']):
            vrf = ep['ep'][ep['ep'].index('/ctx-') + 5 : ep['ep'].index('/cep-')]
        elif re.search('^uni|tn-*./LDevInst-*.', ep['ep']):
            LDevInst = ep['ep'][ep['ep'].index('/LDevInst-') + 10 : ep['ep'].index('/cep-')]
        else:
            raise Exception(f'need to check out the endpoint {ep}')
        
        output.append( 
            {
                "tn":           tn,
                "ep":           ep['ep'],
                "vrf":          vrf,
                "epg":          epg,
                "esg":          esg,
                "host":         ep['host'],
                "mac":          ep['mac'], 
                "addr":         ep['addr'], 
                "fabricPathDn": ep['fabricPathDn'], 
                "desc":         descr,
                "node":         node,
                "physIf":       physIf,
                "pcIf":         pcIf,
                "LDevInst":     LDevInst
            }  
        )
    return { "imdata": output }

def printTable(input=[], mandatory=[]):
    """
    print table-style output
    parameters:
        madatory: Only outputs the values ​​of the specified fields that exist.
    """

    # fields to print - [ (key-name, witdth), ... ]
    # column = [ ("tn", 15), ("vrf", 15), ("epg", 15), ("esg", 15), ("LDevInst", 100), ("host", 20), ("mac", 17), ("addr", 15), ("node", 15), ("physIf", 10), ("pcIf", 30), ("desc", 60) ]  # all fields
    # column = [ ("tn", 15), ("vrf", 15), ("epg", 15), ("esg", 15), ("host", 20), ("mac", 17), ("addr", 15), ("node", 15), ("physIf", 10), ("pcIf", 30), ("desc", 60) ]                     # except - LDevInst
    column = [ ("tn", 15), ("vrf", 15), ("epg", 15), ("host", 20), ("mac", 17), ("addr", 15), ("node", 15), ("physIf", 10), ("pcIf", 30), ("desc", 60) ]                                    # except - esg, LDevInst

    table               = PrettyTable()
    table.field_names   = [ key for key, len in column ]
    table.align         = "l"
    for item in input['imdata']:
        try:
            for key in mandatory:
                item[key][0]
        except:
            continue
        table.add_row([ item[key][:len] for key, len in column ])
    print(table)

def writeCSV(input=[], mandatory=[]):
    """
    print CSV-style output
    """
    
    # fields to print - { "key-name": [], ... }
    csv_data = { "tn": [], "vrf": [], "epg": [], "host": [], "mac": [], "addr": [], "node": [], "physIf": [], "pcIf": [], "desc": [] }  # less fields
    # csv_data = { "tn": [], "vrf": [], "epg": [], "esg": [], "LDevInst": [], "host": [], "mac": [], "addr": [], "node": [], "physIf": [], "pcIf": [], "desc": [] }  # all fields
    csv_file = 'results.csv'

    for item in input['imdata']:
        try:
            for key in mandatory:
                item[key][0]
        except:
            continue
        for key in csv_data.keys():
            value = csv_data[key]
            value.append(item[key])
            csv_data.update({key:value})
    df = pd.DataFrame(csv_data).to_csv(csv_file)
    print(f'{csv_file} file has been created.')

if __name__ == "__main__":
    mandatory = []

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mandatory", default=None, type=str, help="The output includes only the fields separated by commas that have values.")
    args = parser.parse_args()
    if args.mandatory:
        mandatory = [key for key in args.mandatory.split(',')]

    login = auth()
    checkAPICVer(login['version'])
    ep_ip        = get_fvCEp_fvIp()
    infrPortSumm = get_infraPortSummary()
    ep_ip_f      = flatten(ep_ip)
    result       = mapping(ep_ip_f, infrPortSumm)
    
    # print(json.dumps(result))
    printTable(input=result, mandatory=mandatory)
    # writeCSV(input=result, mandatory=mandatory)

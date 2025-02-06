import requests
import os
import sys
import argparse
import json
import re
import warnings
import pandas as pd
from prettytable import PrettyTable


def flatten(imdata):
    output = []
    for item in imdata["imdata"]:
        ep = item["fvCEp"]["attributes"]

        # INFO: infra, mgmt tenants are ignored.
        if "/tn-infra/" in ep["dn"] or "/tn-mgmt/" in ep["dn"]:
            continue

        # INFO: An endpoint can have multiple IP addresses or nothing.
        if "children" in item["fvCEp"]:
            for child in item["fvCEp"]["children"]:
                output.append(
                    {
                        "host": ep["contName"],
                        "mac": ep["mac"],
                        "addr": child["fvIp"]["attributes"]["addr"],
                        "fabricPathDn": child["fvIp"]["attributes"]["fabricPathDn"],
                        "ep": ep["dn"],
                        "bd": ep['bdDn'],
                        "vrf": ep["vrfDn"],
                        'connect': ep['reportingControllerName']
                    }
                )
        else:
            output.append(
                {
                    "host": ep["contName"],
                    "mac": ep["mac"],
                    "addr": "",
                    "fabricPathDn": ep["fabricPathDn"],
                    "ep": ep["dn"],
                    "bd": ep['bdDn'],
                    "vrf": ep["vrfDn"],
                    "connect": ep['reportingControllerName']
                }
            )
    return {"imdata": output}


def mapping(endpoints, portSumm):
    """
    merge the relevant endpoint and interfaces into one row.
    """
    output = []
    for ep in endpoints["imdata"]:
        tn = ep["ep"].split("/")[1][3:]
        bd = ""
        epg = ""
        esg = ""
        vrf = ""
        descr = ""
        pcIf = ""
        physIf = ""
        node = ""
        LDevInst = ""
        connect = ""
        
        connect = ep['connect']

        # INFO: Retrieve description from a dictionary using fabricPathDn
        if ep["fabricPathDn"] != "":
            ep_paths = ep["fabricPathDn"][ep["fabricPathDn"].index("/paths-") + 7 : ep["fabricPathDn"].index("/pathep-")]
            ep_pathep = ep["fabricPathDn"][ep["fabricPathDn"].index("/pathep-[") + 9 : -1]
            node = ep_paths

            for item in portSumm["imdata"]:
                port = item["infraPortSummary"]["attributes"]

                if pcIf == "" and port["pcPortDn"] != "":
                    src = port["pcPortDn"]
                    if "/protpaths-" in src:
                        chk_nodes = src[src.index("/protpaths-") + 11 : src.index("/pathep-")].split("-")
                        chk_path = src[src.index("/pathep-[") + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr = port["description"]
                            physIf = port["portDn"][port["portDn"].index("/pathep-[") + 9 : -1]
                            pcIf = ep_pathep
                    elif "/paths-" in src:
                        chk_nodes = src[src.index("/paths-") + 7 : src.index("/pathep-")]
                        chk_path = src[src.index("/pathep-[") + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr = port["description"]
                            physIf = port["portDn"][port["portDn"].index("/pathep-[") + 9 : -1]
                            pcIf = ep_pathep
                    else:
                        raise Exception(f"{src}")

                elif physIf == "" and port["portDn"] != "":
                    src = port["portDn"]
                    if "/paths-" in src:
                        chk_nodes = src[src.index("/paths-") + 7 : src.index("/pathep-")]
                        chk_path = src[src.index("/pathep-[") + 9 : -1]
                        if ep_paths in chk_nodes and ep_pathep == chk_path:
                            descr = port["description"]
                            physIf = chk_path
                    else:
                        raise Exception(f"{src}")

        try:
            vrf = ep["vrf"][ep["vrf"].index("/ctx-") + 5 :]
        except ValueError:
            # warnings.warn(f"{ep['ep']} has no vrfDn.")
            pass

        if re.search("/epg-", ep["ep"]):
            epg = ep["ep"][ep["ep"].index("/epg-") + 5 : ep["ep"].index("/cep-")]
        elif re.search("/esg-", ep["ep"]):
            esg = ep["ep"][ep["ep"].index("/esg-") + 5 : ep["ep"].index("/cep-")]
        elif re.search("/ctx-", ep["ep"]):
            vrf = ep["ep"][ep["ep"].index("/ctx-") + 5 : ep["ep"].index("/cep-")]
        elif re.search("^uni|tn-*./LDevInst-*.", ep["ep"]):
            LDevInst = ep["ep"][ep["ep"].index("/LDevInst-") + 10 : ep["ep"].index("/cep-")]
        else:
            raise Exception(f"need to check out the endpoint {ep}")

        output.append(
            {
                "tn": tn,
                "ep": ep["ep"],
                "vrf": vrf,
                "bd": bd,
                "epg": epg,
                "esg": esg,
                "host": ep["host"],
                "mac": ep["mac"],
                "addr": ep["addr"],
                "fabricPathDn": ep["fabricPathDn"],
                "desc": descr,
                "node": node,
                "physIf": physIf,
                "pcIf": pcIf,
                "LDevInst": LDevInst,
                "connect": connect
            }
        )
    return output

def ios_network_mapping(network_name, output):
    sections = re.split(r'\n+', output)
    network_info = []
    
    vlan = None
    
    for line in sections:
        if line.startswith("Vlan"):
            vlan = line.split()[0]
        if "Virtual IP address" in line:
            network = line.split()[4]
            if vlan is not None:
                network_info.append(
                    {
                        'vlan' : vlan,
                        'network' : network,
                        'network_name' : network_name
                    }
                )
    
    return network_info

def ios_ip_mapping(host, network_name, output, bd):
    arp_info = []
    mac_info = []
    port_info = []
    
    sections = re.split(r'\n+', output)
    match = re.search(r'Vlan(\d+)', bd)
    if match:
        match_mac = str(match.group(1))
        
    for line in sections:
        if line.startswith("Internet"):
            ip = line.split()[1]
            mac = line.split()[3]
            vlan = line.split()[5]
            arp_info.append(
                {
                    'ip': ip,
                    'mac': mac,
                    'vlan': vlan,
                    # 'host': host,
                    # 'network_name': network_name,
                }
            )
        elif line.startswitch(f"{match_mac}") or line.startswith(f"{match_mac}"):
            mac = line.split()[1]
            port = line.split()[3]
            mac_info.append(
                {
                    'mac': mac,
                    'port': port,
                }
            )
        elif "connected" in line and (line.startswith("Te") or line.startswith("Gi")):
            parts = line.split()
            port = parts[0]
            if len(parts) == 7:
                name = parts[1]
                speed = parts[5]
                porttype = parts[6]
            else:
                name = ""
                speed = parts[4]
                porttype = parts[5]
            port_info.append(
                {
                    'port' : port,
                    'name' : name,
                    'speed' : speed,
                    'porttype' : porttype
                }
            )
            
    port_result = []
    print(mac_info)
    for mac_entry in mac_info:
        for port_entry in port_info:
            if mac_entry['port'] == port_entry['port']:
                port_combined = {
                    'mac': mac_entry['mac'],
                    'port': mac_entry['port'],
                    'name': port_entry['name'],
                    'speed': port_entry['speed'],
                    'porttype': port_entry['porttype'],
                }
                port_result.append(port_combined)
    result = []
    
    #ARP 리스트를 순회하며 MAC 기반으로 Port 데이터 찾기 
    for arp_entry in arp_info:
        for port_result_entry in port_result:
            if arp_entry['mac'] == port_result_entry['mac']:
                #MAC이 동일하면 ARP와 Port 데이터를 결합 
                combined = {
                    'vrf': network_name,
                    'bd': arp_entry['vlan'],
                    'addr': arp_entry['ip'],
                    'mac': arp_entry['mac'],
                    'node': host,
                    'physIf': port_result_entry['port'],
                    'name': port_result_entry['name'],
                    'speed': port_result_entry['speed'],
                    'porttype': port_result_entry['porttype']
                }
                result.append(combined)
    return result
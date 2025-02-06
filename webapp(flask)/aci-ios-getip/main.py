from flask import Flask, render_template, request, redirect, flash, send_file, Response
from concurrent.futures import ThreadPoolExecutor, as_completed
from cryptography.fernet import Fernet
import itertools
import logging
import requests
import socket
import re
import json
import time
import csv
import io
import os
from datetime import datetime
from urllib.parse import quote
from json.decoder import JSONDecoder
from config.session import SessionManager
from config.login import aci_Login, l2_Login
from config.network import aci_bd, aci_findip, aci_findport, ciscol2_net
from config.mapping import flatten, mapping, ios_network_mapping, ios_ip_mapping

app = Flask("GET IP")

session_manager = SessionManager()
session = session_manager.get_session()


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

aci_info = load_and_decrypt_data("encrypted_list.bin")
bdl2_info = load_and_decrypt_data("encrypted_list_bdl2.bin")
sjl2_info = load_and_decrypt_data("encrypted_list_sjl2.bin")

@app.route("/")
def home():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    center = requests.args.get('center', 'BD-APIC')
    bd_info = []
    pattern = r'tn-([A-Za-z0-9_]+)'
    if center == "BD-APIC" or center == "SJ-APIC":
        for aci in aci_info:
            if center == aci['name']:
                token = aci_Login(aci, session)
                bd_result = aci_bd(aci, token, session)
                for item in bd_result:
                    bd = item['fvBD']['attributes']
                    dn = item["fbBD"]["attributes"]["dn"]
                    match = re.search(pattern, dn)
                    info = match.groups()
                    if "children" in item['fvBD']:
                        for child in item['fvBD']['children']:
                            bd_info.append(
                                {
                                    "tn": info[0],
                                    "bd": bd['name']
                                    "subnet": shild['fvSubnet']["attributes"]["ip"],
                                }
                            )
        
        priority = {
            'Operation': 1, 
            'Verification': 2,
            'Development': 3,
            'Management': 4,
            'mgmt': 5,
        }
        sorted_data = sorted(bd_info, key=lambda x: priority.get(x['tn'], float('inf')))
        
        return render_template("home.html", bd_info=sorted_data, center=center)
    else:
        if center == "BD-MGMT":
            devices = load_and_decrypt_data("encrypted_list_bdl2.bin")
        else:
            devices = load_and_decrypt_data("encrypted_list_sjl2.bin")
            
        commands = ["show vrrp"]
        results = []
        networks = []
        
        max_workers = min(32, (os.cpu_count() or 1) + 4)
        logging.info(f"Using {max_workers} threads for SSH connections.")
        
        with ThreadPoolExecutor(max_workers=max_workers) as excutor:
            future_to_device = {
                excutor.submit(ciscol2_net, device['name'], device['network'], device['ip'], device['id'], device['password'], commands): device 
                for device in devices
            }
            
            for future in as_completed(future_to_device):
                device = future_to_device[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    results.append({'host': device['host'], 'output' : None, 'error' : str(exc)})
                    
        for result in results:
            host = result['host']
            if result['error']:
                print(f"Error connecting to {host}: {result['error']}\n")
            elif "State is MASTER" in result['output']:
                network_info = ios_network_mapping(result['network'], result['output'])
                networks.append(network_info)
                
        bd_info = sum(networks, [])
        
        priority = {
            'OOB_MGMT': 1,
            'Internal_MGMT': 2,
            'External_MGMT': 3,
            'DEV/VER_MGMT': 4,
        }
        
        sorted_data = sorted(bd_info, key=lambda x: priority.get(x['network_name'], float('inf')))
        
        return render_template("ios_home.html", bd_info=sorted_data, center=center)

@app.route("/findip")
def findip():
    center = request.args.get('center', 'BD-APIC')
    tenant = request.args.get('tenant')
    serial = request.args.get('serial')
    if center == "BD-APIC" or center == "SJ-APIC":
        bd = request.args.get('bd')
        for aci in aci_info:
            if center == aci['name']:
                token = aci_Login(aci, session)
                ip_result = aci_findip(aci, token, session, tenant, bd, serial)
                ip_data = flatten(ip_result)
                port_data = aci_findport(aci, token, session)
                final_result = mapping(ip_data, port_data)
                sorted_data = sorted([item for item in final_result if item['addr']], key=lambda x: socket.inet_aton(x['addr']))
                sorted_data.extend([item for item in final_result if not item['addr']])
                
        return render_template("findip.html", datas=sorted_data)
    else:
        bd = request.args.get('bd')
        network = request.args.get('network')
        devices = []
        if center == "BD-MGMT":
            device_info = load_and_decrypt_data("encrypted_list_bdl2.bin")
            for item in device_info:
                if item['network'] == network:
                    devices.append(item)
        else:
            device_info = load_and_decrypt_data("encrypted_list_sjl2.bin")
            for item in device_info:
                if item['network'] == network:
                    devices.append(item)
        
        commands = [f"show arp | include {bd}", "show mac address-table", "show interface status"]
        results = []
        ip_data = []
        final_result = []
        max_workers = min(32, (os.cpu_count() or 1) + 4)
        logging.info(f"Using {max_workers} threads for SSH connections.")
        
        with ThreadPoolExecutor(max_workers=max_workers) as excutor:
            future_to_device = {
                excutor.submit(ciscol2_net, device['name'], device['network'], device['ip'], device['id'], device['password'], commands): device 
                for device in devices
            }
            
            for future in as_completed(future_to_device):
                device = future_to_device[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    results.append({'host': device['host'], 'output' : None, 'error' : str(exc)})
                    
        for result in results:
            host = result['host']
            if result['error']:
                print(f"Error connecting to {host}: {result['error']}\n")
            elif "State is MASTER" in result['output']:
                ip_info = ios_ip_mapping(result['name'], result['network'], result['output'], bd)
                final_result.append(ip_info)
                
            sum_data = sum(final_result, [])
            sorted_data = sorted([item for item in sum_data if item['addr']], key=lambda x: socket.inet_aton(x['addr']))
            sorted_data.extend([item for item in sum_data if not item['addr']])
            
            return render_template("ios_findip.html", datas=sorted_data)

@app.route("/export", methods=['POST'])
def export():
    now = datetime.now()
    today_data = now.strftime("%Y-%m-%d")
    datas = request.form.get("data")
    json_string = datas.replace("'", '"')
    parsed_data = json.loads(json_string)
    sorted_data = sorted([item for item in parsed_data if item['addr']], key=lambda x: socket.inet_aton(x['addr']))
    sorted_data.extend([item for item in parsed_data if not item['addr']])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['NO', 'VRF', 'Network', 'IP', 'MAC', 'NODE', 'Interface', 'Host', 'Connect'])
        
    for index, row in enumerate(sorted_data, start=1):
        network = row['bd'] if row['bd'] else 'Serial_Net'
        # connect = row['pcIf'] if row['pcIf'] else row['connect']
        if row['pcIf'] != "":
            connect = row['pcIf']
        elif row['connect'] != "":
            connect = row['connect']
        else:
            connect = "Single Server"
            
        writer.writerow([index, row['vrf'], network, row['addr'], row['mac'], row['node'], row['physIf'], row['host'], connect])
        
    output.seek(0)
    
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=data.csv"})

app.run(0.0.0.0, port=8088)
            
                        

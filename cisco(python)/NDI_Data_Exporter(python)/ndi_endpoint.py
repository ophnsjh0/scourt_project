import http.client
import ssl
import json
from datetime import datetime, timezone, timedelta
import urllib.parse
import re
import os

base_url  = os.getenv('ND_URL')
username  = os.getenv('ND_USERNAME')
password  = os.getenv('ND_PASSWORD')
domain    = os.getenv('ND_DOMAIN')
sslverify = os.getenv('ND_SSLVERIFY')

if base_url == None or username == None or password == None or domain == None:
    print('cannot execute. please check environment variables are valid...')
    exit(1)

conn = None
if sslverify != None and sslverify.lower() == 'false':
    conn = http.client.HTTPSConnection(base_url, context = ssl._create_unverified_context())
elif sslverify != None and sslverify.lower() == 'true':
    conn = http.client.HTTPSConnection(base_url)
else:
    print('invalid environment parameter for ND_SSLVERIFY.')
    exit(1)

filename = f'ndi_endpoint_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
headers  = { "Content-Type": "application/json" }

def auth():
    payload = f'''
        {{
            "domain":     "{domain}",
            "userName":   "{username}",
            "userPasswd": "{password}"
        }}
    '''
    conn.request("POST", "/login.json", payload, headers)
    response = conn.getresponse()
    if response.status == 200:
        headers['Cookie'] = f"AuthCookie={json.loads(response.read().decode())['token']}"
    else:
        raise Exception("auth failed.")
    return

def convertTimestamp(input):
    formatted_time = ''
    if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z', input):
        formatted_time = input
    elif input == 'now':
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    elif re.match('^now-\d+[mhd]$', input):
        current_time = datetime.now(timezone.utc)
        digit = int(input[4:-1])
        unit  = input[-1:]
        if unit == 'd':
            modified_time = current_time - timedelta(days=digit)
        elif unit == 'h':
            modified_time = current_time - timedelta(hours=digit)
        else:
            modified_time = current_time - timedelta(minutes=digit)
        formatted_time = modified_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    else:
        raise Exception('INVALID_TIMESTAMP_FORMAT')
    return formatted_time

def get_endpoint(insightsGroupName='', fabricName='', startTs='now-15m', endTs='now', filter='', count=10000):
    imdata     = []
    offset     = 0
    start_time = convertTimestamp(startTs)
    end_time   = convertTimestamp(endTs)
    attempt    = 1
    while True:
        url =  f'/sedgeapi/v1/cisco-nir/api/api/v1/endpoints'
        url += f'?insightsGroupName={insightsGroupName}'
        url += f'&sort=-anomalyScore'
        url += f'&endTs={end_time}'
        url += f'&startTs={start_time}'
        url += f'&count={count}'
        url += f'&filter={urllib.parse.quote(filter)}'
        url += f'&offset={offset}'
        print(f'\n[{attempt}] Calling... {url}')
        res = conn.request("GET", url, '', headers)
        response = conn.getresponse()
        resbody = json.loads(response.read().decode())
        print(f"received {len(resbody['entries'])} / {resbody['totalItemsCount']} entries.")
        if len(resbody['entries']) == 0:
            break
        for item in resbody['entries']:
            imdata.append(item)
        if offset + int(count) < 10000:
            offset = offset + int(count)
        else:
            break
        attempt = attempt + 1
    return imdata

def csvHeaders():
    main_attr  = [
        'fabricName','tenant','displayVrf','displayEpg','mac','ip','vmName','hypervisor','nodeNames','displayInterface','encap','vpcAttached',
        'modType','anomalyScore','createTime'
        # 'moveType','epHostname', endpointId', 'nodeName','displayBd','bd','vrf','siteName','applicationProfile','vmmSource',
    ]
    headers = {}
    for item in main_attr:
        headers[f'{item}'] = ''
    return headers

def writeCSV(headers=[], entries=[]):
    sep = ';'
    with open(filename, "w") as f:
        f.write(f'sep={sep}\n')
        for header in headers:
            f.write(f'{header}{sep}')
        f.write('\n')
        for item in entries:
            for header in headers:
                try:
                    f.write(f'{item[header]}{sep}')
                except:
                    try:
                        subs = header.split('_')
                        f.write(f'({item[subs[0]][0][subs[1]]}{sep})')
                    except:
                        f.write(f'{sep}')
            f.write('\n')
        print(f'\n{filename} with {len(entries)} record(s) has been created.')

if __name__ == "__main__":
    print('''
=============================================================================
Nexus Dashboard Insights Endpoint Exporter (2024/07/25)
Copyright (c) 2024 Cisco Customer Success and/or its affiliates.
=============================================================================
    ''')
    param = []
    param.append(input('Enter fabricName                 : '))
    param.append(input('Enter startTs [ default: now-1d ]: ') or 'now-1d')
    param.append(input('Enter endTs   [ default: now    ]: ') or 'now')
    param.append(input('Enter filter  [ ex: protocolName:TCP AND flowType:IPv4 AND ip:*192.168* ]: '))

    for idx in range(len(param) - 1):
        if param[idx] == '':
            print('\nentered invalid parameter, then exit...')
            exit(1)

    login = auth()
    data = get_endpoint(insightsGroupName='default', fabricName=param[0], startTs=param[1], endTs=param[2], filter=param[3])
    writeCSV(headers=csvHeaders(), entries=data)
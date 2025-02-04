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

filename = f'ndi_flow_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
headers  = { "Content-Type": "application/json" }

def auth():
    payload = f'''{{"domain": "{domain}", "userName": "{username}", "userPasswd": "{password}"}}'''
    conn.request("POST", "/login.json", payload, headers)
    response = conn.getresponse()
    if response.status == 200:
        headers['Cookie'] = f"AuthCookie={json.loads(response.read().decode())['token']}"
    else:
        raise Exception("auth failed.")
    return

def get_flows(insightsGroupName, fabricName, startTs, endTs, filter, timeslice):
    startTs     = datetime.strptime(convertTimestamp(startTs), "%Y-%m-%dT%H:%M:%S.%fZ")
    endTs       = datetime.strptime(convertTimestamp(endTs), "%Y-%m-%dT%H:%M:%S.%fZ")
    increment   = timedelta(minutes=int(timeslice))

    time_ranges = []
    currentTs   = startTs
    while currentTs < endTs:
        if currentTs + increment < endTs:
            nextTs = currentTs + increment
        else:
            nextTs = endTs
        time_ranges.append({"start": currentTs, "end": nextTs})
        currentTs = nextTs

    attempt = 1
    imdata = []
    for time in time_ranges:
        startTs = time['start'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        endTs   = time['end'].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        flows = call_get_flows(insightsGroupName=insightsGroupName, fabricName=fabricName, startTs=startTs, endTs=endTs, filter=filter, seq=attempt)
        for item in flows:
            imdata.append(item)
        if len(flows) >= 10000:
            print('\nReach the maximum number of items that can be received at one time. Please reduce the time slice and try again.')
            break
        attempt += 1
    return imdata
    
def call_get_flows(insightsGroupName, fabricName, startTs, endTs, filter, seq):
    url =  f'/sedgeapi/v1/cisco-nir/api/api/telemetry/flows/summary.json'
    url += f'?aggrRecords=false'
    url += f'&fabricName={fabricName}'
    url += f'&insightsGroupName={insightsGroupName}'
    url += f'&sort=-ts'
    url += f'&count=10000'
    url += f'&offset=0'
    url += f'&filter={urllib.parse.quote(filter)}'
    url += f'&startTs={startTs}'
    url += f'&endTs={endTs}'
    print(f'\n[{seq}] Calling... {url}')
    res = conn.request("GET", url, '', headers)
    response = conn.getresponse()
    resbody = json.loads(response.read().decode())
    print(f"received {len(resbody['entries'])} item(s).")
    imdata = []
    for item in resbody['entries']:
        imdata.append(item)
    return imdata

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

def csvHeaders():
    main_attr  = [
        'srcIp','dstIp','srcPort','dstPort','protocolName','ingressVrf','egressVrf','flowType','ingressTenant','egressTenant','fabricName','srcEpg','dstEpg'
    ]
    stats_attr = [
        'ingressPktCount','ingressByteCount','egressPktCount','egressByteCount','ingressBurst','ingressBurstMax','egressBurst','egressBurstMax','latency',
        'dropPktCount','dropNodes','dropReasons','paths','nodeNames','ingressNodes','egressNodes','anomalyScore','ingressVif','egressVif','ts', 
        # 'hashCollision','srcMoveCount','dstMoveCount','moveCount','originTs','originDate','terminalTs','terminalDate','flowRecordCount','siteName','fabricName',
        #'srcEpg','dstEpg',
    ]
    headers = {}
    for item in main_attr:
        headers[f'{item}'] = ''
    for attr in stats_attr:
        headers[(f'stats_{attr}')] = ''
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
                        f.write(f'{item[subs[0]][0][subs[1]]}{sep}')
                    except:
                        f.write(f'{sep}')
            f.write('\n')
        print(f'\n{filename} with {len(entries)} record(s) has been created.')

if __name__ == "__main__":
    print('''
=============================================================================
Nexus Dashboard Insights Flow Exporter (2024/07/25)
Copyright (c) 2024 Cisco [Customer Success] and/or its affiliates.
=============================================================================
    ''')
    param = []
    param.append(input('Enter fabricName                             : '))
    param.append(input('Enter startTs           [ default: now-15m ] : ') or 'now-15m')
    param.append(input('Enter endTs             [ default: now     ] : ') or 'now')
    param.append(input('Enter filter            [ ex: protocolName:TCP AND srcIp:10.10.10.10 ]: '))
    param.append(input('Enter time slice (mins) [ default: 15      ] : ') or '15')

    login = auth()
    data = get_flows(insightsGroupName='default', fabricName=param[0], startTs=param[1], endTs=param[2], filter=param[3], timeslice=param[4])
    writeCSV(headers=csvHeaders(), entries=data)
import requests
from datetime import datetime

def log_filter(center):
    filters = []
    if center['startdate'] and center['starttime'] and center['enddate'] and center['endtime']:
        filter.append(f'ge({center["selectlog"]}.created,"{center["startdate"]}T{center["starttime"]}"),le({center["selectlog"]}.created,"{center["enddate"]}T{center["endtime"]}")')
    if center['code']:
        if center['codeselector'] == "eq":
            filters.append(f'eq({center["selectlog"]}.code,"{center["code"]}")')
        else:
            filters.append(f'not(eq({center["selectlog"]}.code,"{center["code"]}"))')
    if center['serverity']:
        filter.append(f'eq({center["selectlog"]}.severity,"{center["severity"]}")')
    if center['descr']:
        filter.append(f'wcard({center["selectlog"]}.descr,"{center["descr"]}")')
    if filters:
        filter_query = ",".join(filters)
        query_params = f"&query-target-filter=and({filter_query})"
    else:
        query_params = ""
    
    return query_params

def aci_mainlog(center, token, session):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    url = f'https://{center[ip]}/api/node/class/faultSummary.json'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        log_data = response.json()['imdata']
    return log_data

def aci_faultlog(center, token, session, page, page_size):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    base_url = f'https://{center["ip"]}/api/node/class/{center['selectlog']}.json?order-by={center["selectlog"]}.created|desc'
    query_params = log_filter(center)
    url = f'{base_url}{query_params}&page-size={page_size}&page={page}'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        log_data = response.json()['imdata']
        return log_data, url
    else:
        error_message = f"error {response.status_code}"
        return error_message
 
## fault 로그와 event 로그 export 로그는 같은 형식으로 처리 가능 아래 삭제 가능 ?? 확인 ##    
def aci_eventlog(center, token, session, page, page_size):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    base_url = f'https://{center["ip"]}/api/node/class/{center['selectlog']}.json?order-by={center["selectlog"]}.created|desc'
    query_params = log_filter(center)
    url = f'{base_url}{query_params}&page-size={page_size}&page={page}'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        log_data = response.json()['imdata']
        return log_data, url
    else:
        error_message = f"error {response.status_code}"
        return error_message
    
def export_log(center, token, session, page, page_size):
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    base_url = f'https://{center["ip"]}/api/node/class/{center['selectlog']}.json?order-by={center["selectlog"]}.created|desc'
    query_params = log_filter(center)
    url = f'{base_url}{query_params}&page-size={page_size}&page={page}'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        log_data = response.json()['imdata']
        return log_data, url
    else:
        error_message = f"error {response.status_code}"
        return error_message
    
    

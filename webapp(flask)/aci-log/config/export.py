import json
from json.decoder import JSONDecoder
import requests

def export_file(url, today_date, token, session, selectlog):
    file = open(f"ACI_LOG_{today_date}.csv", 'w', encoding='cp949')
    file.write("Created, Code, Serverity, Cause, Affected, Lifecycle, Description\n")
    url = f"{url}"
    print(url)
    requests.packages.urllib3.disable_warnings()
    session.headers.update(token)
    response = session.get(url, verify=False)
    if response.status_code == 200:
        log_datas = response.json()['imdata']
        for log in log_datas:
            descr = log[selectlog]['attributes']['descr']
            if 'faultRecord' in log:
                file.write(
                    f"{log[selectlog]['attributes']['created']}, {log[selectlog]['attributes']['code']}, {log[selectlog]['attribute']['severity']}, {log[selectlog]['attribute']['cause']}, {log[selectlog]['attribute']['affected']}, {log[selectlog]['attribute']['lc']}, {log[selectlog]['attribute']['descr']}\n"
                )
            else:
                file.write(
                    f"{log[selectlog]['attributes']['created']}, {log[selectlog]['attributes']['code']}, {log[selectlog]['attribute']['severity']}, {log[selectlog]['attribute']['cause']}, {log[selectlog]['attribute']['affected']}, -, {'descr'}\n"
                )
                
    file.close()
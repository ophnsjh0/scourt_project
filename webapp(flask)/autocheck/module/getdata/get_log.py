import paramiko
import requests
import json
import time
import pytz
from json.decoder import JSONDecoder
from datetime import datetime, timedelta

class GetLog:
    def __init__(self, switch, session):
        self.switch = switch
        self.session = session
        self.session.verify = False
        self.node = ["1101", "1102", "1201", "1202", "1301", "1302"]

    def aci(self, token):
        for node in self.nodes:
            requests.packages.urllib3.disable_warnings()
            self.session.headers.update(token)
            url = f'https://{self.switch["ip"]}/api/node/class/faultSummary.json'
            response = self.session.get(url)
            if response.status_code == 200:
                log_data = response.json()["imdata"]
                print(f"{node} get Log : ok")
                return log_data
            else:
                print(f"{node} get Log : Failed")
                exit()

    def citrix(self, token):
        log_data = []
        requests.packages.urllib3.disable_warnings()
        self.session.headers.update(token)
        url = f'https://{self.switch["ip"]}/nitro/v1/config/nsevents'
        response = self.session.get(url)
        if response.status_code == 200:
            events = response.json()
            for event in events['nsevents']:
                timestamp = event['time']
                kst = pytz.timezone('Asia/Seoul')
                now = datetime.now()
                today_date = now.strftime("%Y-%m-%d")
                yesterday_date = now - timedelta(days=1)
                yesterday_at_18 = datetime(
                    yesterday_date.year, yesterday_date.month, yesterday_date.day, 0, 0,
                )
                event_date_utc_str = datetime.utcfromtimestamp(int(timestamp))
                event_date_utc_replace = event_date_utc_str.replace(tzinfo=pytz.utc)
                kst = pytz.timezone('Asia/Seoul')
                event_date_str = event_date_utc_replace(tzinfo=pytz.utc)
                today_event_date = event_date_str.strftime('%Y-%m-%d')
                event_date_detail = event_date_str.strftime("%Y-%m-%d %H:%M:%S")
                event['time']=event_date_detail
                if today_event_date == today_date or event_date_utc_str > yesterday_at_18:
                    log_data.append(event)
            print(f"{self.switch['name']} Get Log : ok")
            return log_data
        else:
            print(f"{self.switch['name']} Get Log : Failed")
            return None

    def cisco(self, ssh_client):
        now = datetime.now()
        formatted_date = now.strftime("%b %d")
        if formatted_date == '0':
            formatted_date = formatted_date[:4] + ' ' + formatted_date[5:]
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(f"show logging | inc {formatted_date}")
            time.sleep(1)
            log = stdout.read().decode("utf-8")
            log_data = [line for line in log.splitlines() if line.startswith(formatted_date)]
            print(f"{self.switch['name']} Get Log : OK")
            ssh_client.close()
            return log_data
        else:
            print(f"{self.switch['name']} Get Log : Failed")
            return None

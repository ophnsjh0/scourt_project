from flask import Flask, render_template, request, redirect, flash, send_file
from cryptography.fernet import Fernet
import requests
import json
import time
from datetime import datetime
from urllib.parse import quote
from json.decoder import JSONDecoder
from config.session import SessionManager
from config.login import aci_Login
from config.log import aci_mainlog, aci_faultlog, aci_eventlog
from config.export import export_file

app = Flask("ACI_LOG")

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

db = load_and_decrypt_data("encrypted_list.bin")

@app.route("/")
def home():
    main_log = []
    for i in db:
        token = aci_Login(i, session)
        log_data = aci_mainlog(i, token, session)
        page = int(request.args.get('page', 0))
        page_size = int(request.args.get('page_size', 10))
        next_page = page + 1 if len(main_log) == page_size else None
        prev_page = page - 1 if page > 0 else None
        for log in log_data:
            log['faultSummary']['attributes']['center'] = str(f'{i["name"]}')
        main_log.append(log_data)
    return render_template("home.html", log_data=main_log, page=page, page_size=page_size, next_page=next_page, prev_page=prev_page)

@app.route("/searchlog")
def log():
    selectinfo = dict()
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', 10))
    ## 분당 세종을 변수 처리하여 2번 반복하지 않고 하나에 코드로 처리 가능 확인 필요 ## 
    for i in db:
        if request.args.get("center") == "bundang":
            if i['name'] == 'BD-APIC':
                i['cneter'] = request.args.get("center")
                i["startdate"] = request.args.get("startdate")
                i["enddate"] = request.args.get("enddate")
                i["starttime"] = request.args.get("starttime")
                i["endtime"] = request.args.get("endtime")
                i["selectlog"] = request.args.get("selectlog")
                i["code"] = request.args.get("code")
                i["codeselector"] = request.args.get("codeselector")
                i["severity"] = request.args.get("severity")
                i["descr"] = request.args.get("descr")

                if request.args.get("selectlog") == "faultRecord":
                    token = aci_Login(i, session)
                    full_data = aci_faultlog(i, token, session, page, page_size)
                    log_data = full_data[:-1][0]
                    url_data = full_data[-1]
                    encoded_url = quote(url_data, sage='')
                    print(encoded_url)
                    selected_info = i
                    next_page = page + 1 if len(log_data) == page_size else None
                    prev_page = page - 1 if page > 0 else None

                if request.args.get("selectlog") == "eventRecord":
                    token = aci_Login(i, session)
                    full_data = aci_eventlog(i, token, session, page, page_size)
                    log_data = full_data[:-1][0]
                    url_data = full_data[-1]
                    encoded_url = quote(url_data, sage='')
                    selected_info = i
                    next_page = page + 1 if len(log_data) == page_size else None
                    prev_page = page - 1 if page > 0 else None
        else:
            if i['name'] == 'SJ-APIC':
                i["cneter"] = request.args.get("center")
                i["startdate"] = request.args.get("startdate")
                i["enddate"] = request.args.get("enddate")
                i["starttime"] = request.args.get("starttime")
                i["endtime"] = request.args.get("endtime")
                i["selectlog"] = request.args.get("selectlog")
                i["code"] = request.args.get("code")
                i["codeselector"] = request.args.get("codeselector")
                i["severity"] = request.args.get("severity")
                i["descr"] = request.args.get("descr")

                if request.args.get("selectlog") == "faultRecord":
                    token = aci_Login(i, session)
                    full_data = aci_faultlog(i, token, session, page, page_size)
                    log_data = full_data[:-1][0]
                    url_data = full_data[-1]
                    encoded_url = quote(url_data, sage="")
                    print(encoded_url)
                    selected_info = i
                    next_page = page + 1 if len(log_data) == page_size else None
                    prev_page = page - 1 if page > 0 else None

                if request.args.get("selectlog") == "eventRecord":
                    token = aci_Login(i, session)
                    full_data = aci_eventlog(i, token, session, page, page_size)
                    log_data = full_data[:-1][0]
                    url_data = full_data[-1]
                    encoded_url = quote(url_data, sage="")
                    selected_info = i
                    next_page = page + 1 if len(log_data) == page_size else None
                    prev_page = page - 1 if page > 0 else None
    if log_data == "code_error":
        return redirect("/")
    else:
        return render_template("log.html", log_data=log_data, selected_info=selected_info, page=page, page_size=page_size, next_page=next_page, prev_page=prev_page, url_data=encoded_url)

@app.route("/export")
def export():
    i = dict()
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    url = request.args.get('url')
    url_split = url.split('/')[6]
    url_record = url_split.split('?')[0]
    selectlog = url_record.split('.')[0]
    for i in db:
        if request.args.get("center")  == "sejong":
            if i['name'] == 'SJ-APIC':
                token = aci_Login(i, session)
                export_file(url, today_date, token, session, selectlog)
        else:
            if i["name"] == "BD-APIC":
                token = aci_Login(i, session)
                export_file(url, today_date, token, session, selectlog)
    
    return send_file(f"ACI_LOG_{today_date}.csv", as_attachment=True)

app.run("0.0.0.0")


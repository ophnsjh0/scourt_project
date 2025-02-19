from flask import Flask, render_template, request, redirect, flash, send_file, Response
from module.fuction.autocheck import autocheck_mo, logcheck_mo
from module.fuction.export_file import File
from module.fuction.compare import CompareResult
import time
from datetime import datetime, timedelta

pharse_result = []
log_result = []
switchs = [
    {
        "name": "Ciscospine01",
        "ip": "10.10.10.10",
        "id": "admin",
        "password": "1234qwer",
        "model": "cisco",
    },
    {
        "name": "Ciscospine01",
        "ip": "10.10.10.10",
        "id": "admin",
        "password": "1234qwer",
        "model": "cisco",
    },
]

class AutoCheck:
    def __init__(self):
        self.file = File()
        self.compare = CompareResult()

    def home(self):
        return render_template("home.html")

    def autocheck_run(self):
        select = request.args.get("vendor")
        if select == None:
            return redirect("/")
        elif select == ("citrix"):
            all_data = autocheck_mo(switchs, select)
            self.file.citrix_raw_date(all_data)
            result_data = self.compare.citrix_compare(all_data)
            return render_template(
                "citrix_check.html",
                all_data=all_data,
                result_data=result_data,
                vendor=select,
            )
        elif select == ("cisco"):
            all_data = autocheck_mo(switchs, select)
            self.file.cisco_raw_data(all_data)
            result_data = self.compare.cisco_compare(all_data)
            return render_template(
                "cisco_check.html",
                all_data=all_data,
                result_data=result_data,
                vendor=select,
            )

    def view_log(self):
        switch_ip = request.args.get("switch_ip")
        vendor = request.args.get("vendor")
        hostname = request.args.get("hostname")
        log_data = logcheck_mo(switchs, switch_ip, vendor)
        if vendor == None:
            return redirect("/")
        elif vendor == ("citrix"):
            return render_template("view_citrix_log.html", log_data=log_data, hostname=hostname)
        elif vendor == ("cisco"):
            return render_template("view_cisco_log.html", log_data=log_data, hostname=hostname)

    def save_to_file(self):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        select = request.args.get("vendor")
        if select == None:
            return redirect("/")
        elif select == ("citrix"):
            file_path = fr'C:\raw_data'
            all_data = autocheck_mo(switchs, select)
            result_data = self.compare.citrix_compare(all_data)
            self.file.citrix_to_file(all_data, result_data, select)
            return send_file(file_path, as_attachment=True)
        elif select == ("cisco"):
            file_path = rf"C:\raw_data"
            all_data = autocheck_mo(switchs, select)
            result_data = self.compare.cisco_compare(all_data)
            self.file.cisco_to_file(all_data, result_data, select)
            return send_file(file_path, as_attachment=True)

app = Flask("AutoCheck")

auto_check_instance = AutoCheck()

app.add_url_rule("/", view_func=auto_check_instance.home)
app.add_url_rule("/autocheck", view_func=auto_check_instance.autocheck_run)
app.add_url_rule("/autocheck/log", view_func=auto_check_instance.view_log)
app.add_url_rule("/autocheck/export", view_func=auto_check_instance.save_to_file)

if __name__ == "__main__":
    app.run("0.0.0.0")
    

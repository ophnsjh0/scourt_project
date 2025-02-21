import time
from datetime import datetime, timedelta

class File:
    def __init__(self):
        pass

    def citrix_to_file(self, all_data, result_data, vendor):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = fr'D:\일일점검결과\{vendor}_{today_date}.csv'
        file = open(file_path, 'w', encoding='cp949')
        file.write(
            "장비정보, 장비정보, 장비정보, Resource, Resource, Resource, Interface, Interface, Interface, Interface, Interface, Interface, Interface, SLB_Info, SLB_Info, SLB_Info, SLB_Info, SLB_Info\n"
        )
        file.write("Hostname, IP, Model, CPU_Use, MEM_Use, 결과, 1G_up, 1G_down, 10G_up, 10G_down, ch_up, ch_down, 결과, Vserver_up, Vserver_down, Service_up, Service_down, 결과\n")
        for data in all_data:
            for result in result_data:
                if data['Hostname'] == result['hostname']:
                    file.write(
                        f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {result['resource']}, {data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}, {result['interface']}, {data['Vserver_up']}, {data['Vserver_down']}, {data['Service_up']}, {data['Service_down']}, {result['slbinfo']}\n"
                    )
        file.close()

    def cisco_to_file(self, all_data, result_data, vendor):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = rf"D:\일일점검결과\{vendor}_{today_date}.csv"
        file = open(file_path, "w", encoding="cp949")
        file.write(
            "장비정보, 장비정보, 장비정보, Resource, Resource, Resource, Power, Power, Power, Temperature, Temperature, Temperature, Temperature, FAN, FAN, FAN, FAN, FAN, FAN Interface, Interface, Interface, Interface, Interface, Interface, Interface\n"
        )
        file.write(
            "Hostname, IP, Model, CPU_Use, MEM_Use, 결과, Power_1A, Power_1B, 결과, Inlet, Outlet, Hotspot, 결과, FAN1, FAN2, FAN3, FAN4, FAN5, 결과, 1G_up, 1G_down, 10G_up, 10G_down, ch_up, ch_down, 결과\n"
        )
        for data in all_data:
            for result in result_data:
                if data["Hostname"] == result["hostname"]:
                    if 'FAN3' in data:
                        file.write(
                            f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {result['resource']}, {data['Power_1A']}, {data['Power_1B']}, {result['power']}, {data['Inlet']}, {data['Outlet']}, {data['Hotspot']}, {result['temp']}, {data['FAN1']}, {data['FAN2']}, {data['FAN3']}, {data['FAN4']}, {data['FAN5']}, {result['fan']}, {data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}, {result['interface']}\n"
                        )
                    else:
                        file.write(
                            f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {result['resource']}, {data['Power_1A']}, {data['Power_1B']}, {result['power']}, {data['Inlet']}, {data['Outlet']}, {data['Hotspot']}, {result['temp']}, {data['FAN1']}, {data['FAN2']}, -, -, -, {result['fan']}, {data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}, {result['interface']}\n"
                        )
        file.close()

    def citrix_raw_data(self, all_data):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = fr"D:\일일점검결과\citrix_raw_data_{today_date}.csv"
        file = open(file_path, "w", encoding="cp949")
        for data in all_data:
            file.write(
                f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}, {data['Vserver_up']}, {data['Vserver_down']}, {data['Service_up']}, {data['Service_down']}\n"
            )
        file.close()

    def cisco_raw_data(self, all_data):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = rf"D:\일일점검결과\cisco_raw_data_{today_date}.csv"
        file = open(file_path, "w", encoding="cp949")
        for data in all_data:
            if 'FAN3' in data:
                file.write(
                    f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {data['Power_1A']}, {data['Power_1B']}, {data['Inlet']}, {data['Outlet']}, {data['Hotspot']}, {data['FAN1']}, {data['FAN2']}, {data['FAN3']}, {data['FAN4']}, {data['FAN5']},{data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}\n"
                )
            else:
                file.write(
                    f"{data['Hostname']}, {data['Ip']}, {data['Model']}, {data['CPU_Use']}, {data['MEM_Use']}, {data['Power_1A']}, {data['Power_1B']}, {data['Inlet']}, {data['Outlet']}, {data['Hotspot']}, {data['FAN1']}, {data['FAN2']}, -, -, -, {data['1G_up']}, {data['1G_down']}, {data['10G_up']}, {data['10G_down']}, {data['ch_up']}, {data['ch_down']}\n"
                )
        file.close()

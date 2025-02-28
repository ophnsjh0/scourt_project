import time
from datetime import datetime, timedelta

class File:
    def __init__(self):
        pass

    def aci_l3out(self, all_data):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = rf"C:\l3out_param_{today_date}.csv"
        file = open(file_path, 'w', encoding='utf-8')
        file.write("Tenant, BD, L3Out, Interface, Route, Next_Hop\n")
        for data in all_data:
            file.write(
                f"{data[2]}, {data[0]}, {data[1]}, {data[3]}, {data[4]}, {data[5]}\n"
            )
        file.close()

    def aci_vrf(self, all_data):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = rf"C:\vrf_param_{today_date}.csv"
        file = open(file_path, "w", encoding="utf-8")
        file.write("Tenant, VRF, Preference, Direction, BD Enforcement, IP Data-Plane\n")
        for data in all_data:
            file.write(
                f"{data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}\n"
            )
        file.close()

    def aci_bd(self, all_data):
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        file_path = rf"C:\bd_param_{today_date}.csv"
        file = open(file_path, "w", encoding="utf-8")
        file.write(
            "Tenant, BD, Type, Advertise Host Routes, VRF, L2 Unkown unicast, Dest Flooding, Unicast Routing, ARP Flooding, IP DP Learning, MAC, Subnet, limitIpLearnToSubnets, epMoveDetectMode, IP Data-Plane\n"
        )
        for data in all_data:
            file.write(
                f"{data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}, {data[6]}, {data[7]}, {data[8]}, {data[9]}, {data[10]}, {data[11]}, {data[12]}, {data[13]}, {data[14]}\n"
            )
        file.close()
        
        
        

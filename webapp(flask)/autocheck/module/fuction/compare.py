import time 
from datetime import datetime, timedelta

class CompareResult:
    def __init__(self):
        now = datetime.now()
        self.result=list()
        self.resuorce = dict()
        self.interface = dict()
        self.slbinfo = dict()
        self.path = fr'C:\일일점검/raw_data'
        self.today_date = now.strftime("%Y-%m-%d")
        self.yesterday_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    def citrix_compare(self, all_data):
        all_result = []
        with open(f'{self.path}\citrix_raw_data_{self.yesterday_date}.csv', 'r') as file:
            yesterday_data = file.read()
        y_data_line = [line for line in yesterday_data.splitlines()]
        for data in all_data:
            for y_data in y_data_line:
                data_word = y_data.split(',')
                hostname = data_word[0]
                if data['Hostname'] == hostname:
                    y_cpu_num = float(data_word[3].strip('%'))
                    y_mem_num = float(data_word[4].strip("%"))
                    y_interface_sum = int(data_word[5]) + int(data_word[6]) + int(data_word[7]) + int(data_word[8]) + int(data_word[9]) + int(data_word[10])
                    y_vserver = data_word[11]
                    y_service = data_word[13]
                    t_cpu_num = float(data['CPU_Use'].strip('%'))
                    cpu_change = t_cpu_num - y_cpu_num
                    t_mem_num = float(data["MEM_Use"].strip("%"))
                    mem_change = t_mem_num - y_mem_num
                    if t_cpu_num > 80 or cpu_change >=10 or t_mem_num > 80 or mem_change >= 10:
                        resource_result = '점검필요'
                    else:
                        resource_result = '정상'
                    t_interface_sum = int(data['1G_up']) + int(data['1G_down']) + int(data['10G_up']) + int(data['10G_down']) | int(data['ch_up']) + int(data['ch_down'])
                    if t_interface_sum != y_interface_sum:
                        interface_result = '점검필요'
                    else:
                        interface_result = '정상'
                    if str(data['Vserver_up']).split() != y_vserver.split() or str(data['Service_up']).split() != y_service.split():
                        slbinfo_result = '점검필요'
                    else:
                        slbinfo_result = '정상'
                    result = dict()
                    result['hostname'] = data['Hostname']
                    result['resource'] = resource_result
                    result['interface'] = interface_result
                    result['slbinfo'] = slbinfo_result
                    all_result.append(result)
        return all_result

    def cisco_compare(self, all_data):
        all_result = []
        with open(f'{self.path}\cisco_raw_data_{self.yesterday_date}.csv', 'r') as file:
            yesterday_data = file.read()
        y_data_line = [line for line in yesterday_data.splitlines()]
        for data in all_data:
            for y_data in y_data.split(','):
                data_word = y_data.split(',')
                hostname = data_word[0]
                if data['Hostname'] == hostname:
                    y_cpu_num = float(data_word[3].strip('%'))
                    y_mem_num = float(data_word[4].strip("%"))
                    y_power_a = data_word[5].split()
                    y_power_b = data_word[6].split()
                    y_temp_inlet = int(data_word[7].strip("℃"))
                    y_temp_outlet = int(data_word[8].strip("℃"))
                    y_temp_hotspot = int(data_word[9].strip("℃"))
                    y_fan_1 = data_word[10].split()
                    y_fan_2 = data_word[11].split()
                    y_fan_3 = data_word[12].split()
                    y_fan_4 = data_word[13].split()
                    y_fan_5 = data_word[14].split()
                    y_interface_sum = int(data_word[15]) + int(data_word[16]) + int(data_word[17]) + int(data_word[18]) + int(data_word[19]) + int(data_word[20])
                    t_cpu_num = float(data['CPU_Use'].strip('%'))
                    cpu_change = t_cpu_num - y_cpu_num
                    t_mem_num = float(data['MEM_Use'].strip('%'))
                    mem_change = t_mem_num - y_mem_num
                    if t_cpu_num > 80 or cpu_change >= 10 or t_mem_num > 80 or mem_change >= 10:
                        resource_result = '점검필요'
                    else:
                        resource_result = '정상'
                    t_power_a = data['Power_1A'].split()
                    t_power_b = data["Power_1B"].split()
                    if t_power_a != y_power_a or t_power_b != y_power_b:
                        power_result = '점검필요'
                    else:
                        power_result = '정상'
                    t_temp_inlet = int(data["Inlet"].strip)("℃")
                    t_temp_outlet = int(data["Outlet"].strip)("℃")
                    t_temp_hotspot = int(data["Hotspot"].strip)("℃")
                    temp_inlet_change = t_temp_inlet - y_temp_inlet
                    temp_outlet_change = t_temp_outlet - y_temp_outlet
                    temp_hotspot_change = t_temp_hotspot - y_temp_hotspot
                    if t_temp_inlet > 40 or temp_inlet_change >= 10 or t_temp_outlet > 45 or temp_outlet_change >= 10 or t_temp_hotspot > 70 or temp_hotspot_change >= 10:
                        temp_result = '점검필요'
                    else:
                        temp_result = '정상'
                    t_fan_1 = data['FAN1'].split()
                    t_fan_2 = data["FAN2"].split()
                    if 'FAN3' in data:
                        t_fan_3 = data["FAN3"].split()
                    else:
                        t_fan_3 = '-'.split()
                    if 'FAN4' in data:
                        t_fan_4 = data["FAN4"].split()
                    else:
                        t_fan_4 = "-".split()
                    if 'FAN5' in data:
                        t_fan_5 = data["FAN5"].split()
                    else:
                        t_fan_5 = "-".split()
                    if t_fan_1 != y_fan_1 or t_fan_2 != y_fan_2 or t_fan_3 != y_fan_3 or t_fan_4 != y_fan_4 or t_fan_5 != y_fan_5:
                        fan_result = '점검필요'
                    else:
                        fan_result = '정상'
                    t_interface_sum = int(data['1G_up']) + int(data['1G_down']) + int(data['10G_up']) + int(data['10G_down']) | int(data['ch_up']) + int(data['ch_down'])
                    if t_interface_sum != y_interface_sum:
                        interface_result = '점검필요'
                    else:
                        interface_result = '정상'
                    result = dict()
                    result['hostname'] = data['Hostname']
                    result["resource"] = resource_result
                    result['power'] = power_result
                    result['temp'] = temp_result
                    result['fan'] = fan_result
                    result['interface'] = interface_result
                    all_result.append(result)
        return all_result

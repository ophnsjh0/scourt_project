import re


class AutocheckParser:
    def __init__(
        self,
        switch,
        general_data,
        cpu_data,
        mem_data,
        power_data,
        temp_data,
        interface_data,
        fan_data,
    ):
        self.switch = switch
        self.general_data = general_data
        self.cpu_data = cpu_data
        self.mem_data = mem_data
        self.power_data = power_data
        self.temp_data = temp_data
        self.interface_data = interface_data
        self.fan_data = fan_data
        self.result = list()

    def ciscoparser(self):
        general = dict()
        general_line = [
            line
            for line in self.general_data.splitlines()
            if "Motherboard Serial Number" in line
            or "Model Nuber" in line
            or "System Serial Number" in line
            or "*" in line
        ]
        general_word = [word for pharse in general_line for word in pharse.split()]
        general["Hostname"] = self.switch["name"]
        general["Ip"] = self.switch["ip"]
        general["Serial"] = general_word[4]
        general["Model"] = general_word[8]
        general["Version"] = general_word[18]

        cpu = dict()
        cpu_line = [
            line for line in self.cpu_data.splitlines() if "CPU utilization" in line
        ]
        cpu_word = [word for pharse in cpu_line for word in pharse.split()]
        cpu["CPU_Use"] = cpu_word[11]

        mem = dict()
        mem_line = [line for line in self.mem_data.splitlines() if "Processor" in line]
        mem_word = [word for pharse in mem_line for word in pharse.split()]
        mem["MEM_Use"] = f"{round(int(mem_word[3]) / int(mem_word[2]) * 100, 1)}%"

        power = dict()
        power_line = [
            line
            for line in self.power_data.splitlines()
            if line.startswith("1A") or line.startswith("1B")
        ]
        power_word = [word for pharse in power_line for word in pharse.split()]
        power["Power_1A"] = power_word[3]
        power["Power_1B"] = power_word[10]

        temp = dict()
        temp_line = [
            line
            for line in self.temp_data.splitlines()
            if line.startswith("Inlet")
            or line.startswith("Outlet")
            or line.startswith("Hotspot")
        ]
        temp_word = [word for pharse in temp_line for word in pharse.split()]
        temp["Inlet"] = f"{temp_word[3]}℃"
        temp["Outlet"] = f"{temp_word[9]}℃"
        temp["Hotspot"] = f"{temp_word[15]}℃"

        interface = dict()
        gi_up_pattern = r"^Gi.*connected"
        gi_down_pattern = r"^Gi.*(disabled|notconnect)"
        te_up_pattern = r"^Te.*connected"
        te_down_pattern = r"^Te.*(disabled|notconnect)"
        po_up_pattern = r"^Po.*connected"
        po_down_pattern = r"^Po.*(disabled|notconnect)"
        interface["1G_up"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(gi_up_pattern, line)
        )
        interface["1G_down"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(gi_down_pattern, line)
        )
        interface["10G_up"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(te_up_pattern, line)
        )
        interface["10G_down"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(te_down_pattern, line)
        )
        interface["ch_up"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(po_up_pattern, line)
        )
        interface["ch_down"] = sum(
            1
            for line in self.interface_data.splitlines()
            if re.search(po_down_pattern, line)
        )

        fan = dict()
        fan_line = [
            line for line in self.fan_data.splitlines() if "Front to Back" in line
        ]
        for fan_detail in fan_line:
            fan_word = fan_detail.split()
            fan[f"FAN{str(fan_word[1])}"] = fan_word[3]

        self.result = general | cpu | mem | power | temp | interface | fan
        return self.result

    def citrixparser(self, vserver_data, service_data, log_data):
        general = dict()
        general["Hostname"] = self.switch["name"]
        general["Ip"] = self.general_data[2]["ipaddress"]
        general["Serial"] = self.general_data[1]["serialno"]
        model_name = self.general_data[1]["hwdescription"].split()
        general["Model"] = model_name[-1]
        version_info = self.general_data[0]["version"].split()
        general["Version"] = f"{version_info[1]} {version_info[2]} {version_info[3]}"

        cpu = dict()
        if int(self.cpu_data["cpuusagepcnt"]) == int(4294967295.0):
            cpu["CPU_Use"] = f"{str(self.cpu_data['pktcpuusagepcnt'])}%"
        else:
            cpu["CPU_Use"] = f"{str(self.cpu_data['cpuusagepcnt'])}%"

        mem = dict()
        # mem["MEM_Use"] = f"{str(self.mem_data['resmemusage'])}%"
        mem["MEM_Use"] = f"{str(round(self.mem_data['memusagepcnt'], 1))}%"

        interface = dict()
        interface["1G_up"] = sum(
            1
            for line in self.interface_data
            if (line["id"].startswith("0") or line["id"].startswith("1"))
            and line["curintfstate"] == "UP"
        )
        interface["1G_down"] = sum(
            1
            for line in self.interface_data
            if (line["id"].startswith("0") or line["id"].startswith("1"))
            and line["curintfstate"] == "DOWN"
        )
        interface["10G_up"] = sum(
            1
            for line in self.interface_data
            if (line["id"].startswith("25") or line["id"].startswith("10"))
            and line["curintfstate"] == "UP"
        )
        interface["10G_down"] = sum(
            1
            for line in self.interface_data
            if (line["id"].startswith("25") or line["id"].startswith("10"))
            and line["curintfstate"] == "DOWN"
        )
        interface["ch_up"] = sum(
            1
            for line in self.interface_data
            if line["id"].startswith("LA") and line["curintfstate"] == "UP"
        )
        interface["ch_down"] = sum(
            1
            for line in self.interface_data
            if line["id"].startswith("LA") and line["curintfstate"] == "DOWN"
        )

        slb = dict()
        slb["Vserver_up"] = sum(
            1 for line in vserver_data if line["curstate"] == "UP"
        )
        slb["Vserver_down"] = sum(
            1 for line in vserver_data if line["curstate"] == "DOWN"
        )
        slb["Service_up"] = sum(
            1 for line in vserver_data if line["svrstate"] == "UP"
        )
        slb["Service_down"] = sum(
            1 for line in vserver_data if line["svrstate"] == "DOWN"
        )
        # slb["Service_up"] = sum(
        #     1 for line in vserver_data if line["curstate"] == "UP"
        # )
        # slb["Service_down"] = sum(
        #     1 for line in vserver_data if line["curstate"] == "DOWN"
        # )
        
        log=dict()
        log_result = []
        for log_info in log_data:
            log_form=dict()
            log_form['time']=log_info['time']
            log_form['text']=log_info['text']
            log_result.append(log_form)
        log['LOG']=log_result
        
        self.result = general | cpu | mem | interface | slb | log
        return self.result

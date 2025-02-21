from module.session.session_manager import SessionManager
from module.login.login import Login
from module.logout.logout import Logout
from module.getdata.get_interface import GetInterface
from module.getdata.get_cpu import GetCpu
from module.getdata.get_mem import GetMem
from module.getdata.get_log import GetLog
from module.getdata.get_general import GetGeneral
from module.getdata.get_fan import GetFan
from module.getdata.get_power import GetPower
from module.getdata.get_temp import GetTemp
from module.getdata.get_slb import GetSlb
from module.parser.autocheck_parser import AutocheckParser

def autocheck_mo(switchs, select):
    pharse_result = []
    for switch in switchs:
        session_manager = SessionManager()
        session = session_manager.get_session()
        login = Login(switch, session)
        logout = Logout(switch, session)
        interface = GetInterface(switch, session)
        cpu = GetCpu(switch, session)
        mem = GetMem(switch, session)
        log = GetLog(switch, session)
        general = GetGeneral(switch, session)
        fan = GetFan(switch, session)
        power = GetPower(switch, session)
        temp = GetTemp(switch, session)
        slb = GetSlb(switch, session)

        if switch['model']  == select and switch['model'] == 'aci':
            token = login.aci()
            interface_data = interface.aci(token)
            cpu_data = cpu.aci(token)
            mem_data = mem.aci(token)
            log_data = log.aci(token)
            general_data = general.aci(token)
            fan_data = fan.aci(token)
            power_data = power.aci(token)
            temp_data = temp.aci(token)
            logout.aci()
        elif switch['model'] == select and switch['model'] == 'citrix':
            token = login.citrix()
            general_data = general_data(token)
            cpu_data = cpu.citrix(token)
            mem_data = mem.citrix(token)
            fan_data = dict()
            power_data = dict()
            temp_data = dict()
            log_data = log.citrix(token)
            vserver_data = slb.vserver(token)
            service_data = slb.service(token)
            # service_binding_data = slb.service(token, vserver_data)
            interface_data = interface.citrix(token)
            logout.citrix()
            parser = AutocheckParser(switch, general_data, cpu_data, mem_data, power_data, temp_data, interface_data, fan_data)
            parsing_data = parser.citrixparser(vserver_data, service_data, log_data)
            pharse_result.append(parsing_data)
        elif switch['model'] == select and switch['model'] == 'cisco':
            ssh_client = login.cisco()
            general_data = general.cisco(ssh_client)
            ssh_client = login.cisco()
            cpu_data = cpu.cisco(ssh_client)
            ssh_client = login.cisco()
            mem_data = mem.cisco(ssh_client)
            ssh_client = login.cisco()
            power_data = log.citrix(ssh_client)
            ssh_client = login.cisco()
            temp_data = temp.cisco(ssh_client)
            ssh_client = login.cisco()
            interface_data = interface.cisco(ssh_client)
            ssh_client = login.cisco()
            fan_data = fan.cisco(ssh_client)
            ssh_client = login.cisco()
            log_data = log.cisco(ssh_client)
            ssh_client = login.cisco()
            parser = AutocheckParser(switch, general_data, cpu_data, mem_data, power_data, temp_data, interface_data, fan_data)
            parsing_data = parser.ciscoparser()
            pharse_result.append(parsing_data)
    return pharse_result

def logcheck_mo(switchs, switch_ip, vendor):
    log_result = []
    for switch in switchs:
        session_manager = SessionManager()
        session = session_manager.get_session()
        login = Login(switch, session)
        logout = Logout(switch, session)
        log = GetLog(switch, session)
        if switch['ip'] == switch_ip and switch['model'] == 'aci':
            token = login.aci()
            log_data = log.aci(token)
            print(log_data)
            logout.aci
        elif switch['ip'] == switch_ip and switch['model'] == 'citrix':
            token = login.citrix()
            log_data = log.citrix(token)
            logout.citrix()
            return log_data
        elif switch['ip'] == switch_ip and switch['model'] == 'cisco':
            ssh_client = login.cisco()
            log_data = log.cisco(ssh_client)
            return log_data

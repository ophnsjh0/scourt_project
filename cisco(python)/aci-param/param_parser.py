import re
from collections import OrderedDict

class ParamParser:
    def __init__(self, l3out, bd_to_l3out, vrf, bd_to_vrf):
        self.l3out = l3out
        self.bd_to_l3out = bd_to_l3out
        self.vrf = vrf 
        self.bd_to_vrf = bd_to_vrf 

    def aci_l3out_parser(self):
        bd_to_l3out_result = []
        for item in self.bd_to_l3out:
            bd_name = item['fvBD']['attributes']['name']
            if 'children' in item['fvBD']:
                for item in item['fvBD']['children']:
                    l3out = item['fvRsBDToOut']['attributes']['tnL3extOutName']
                    bd_to_l3out_result.append((bd_name, l3out))
            else:
                bd_to_l3out_result.append((bd_name, 'N/A'))
        data_result = []
        pattern = r'tn-([A-Za-z0-9_]+)/out-([A-Za-z0-9_]+)'
        for item in self.l3out:
            dn = item['l3extOut']['attributes']['dn']
            match = re.search(pattern, dn)
            info = match.groups()
            tenant=info[0]
            l3extOut = item['l3extOut']
            l3extOut_name = l3extOut['attributes']['name']
            if 'children' in l3extOut:
                for l3extLNodeP in l3extOut['children']:
                    for l3extRsNodeL3OutAtt in l3extLNodeP['l3extLNodeP']['children']:
                        interface = l3extRsNodeL3OutAtt['l3extRsNodeL3OutAtt']['attributes']['rtrId']
                        if 'children' in l3extRsNodeL3OutAtt['l3extRsNodeL3OutAtt']:
                            for ipRouteP in l3extRsNodeL3OutAtt['l3extRsNodeL3OutAtt']['children']:
                                route = ipRouteP["ipRouteP"]["attributes"]['ip']
                                for ipNexthopP in ipRouteP['ipRouteP']['children']:
                                    next_hop = ipNexthopP["ipNexthopP"]["attributes"]['nhAddr']
                                    data_result.append((tenant, l3extOut_name, interface, route, next_hop))

        l3out_result = []
        for bd in bd_to_l3out_result:
            if bd[1] == l3out[1]:
                merge = list(OrderedDict.fromkeys(bd + l3out))
                l3out_result.append(merge)
        l3out_result.sort(key=lambda x: x[0])

        return l3out_result

    def aci_vrf_parser(self):
        vrf_result = []
        pattern = r'tn-([A-Za-z0-9_]+)'
        for item in self.vrf:
            dn = item['fvCtx']['attributes']['dn']
            match = re.search(pattern, dn)
            info = match.group()
            tenant = info[0]
            vrf = item["fvCtx"]["attributes"]['name']
            prference = item["fvCtx"]["attributes"]['pcEnfPref']
            direction = item["fvCtx"]["attributes"]['pcEnfDir']
            dbenforce = item["fvCtx"]["attributes"]['bdEnforcedEnable']
            ipdata = item["fvCtx"]["attributes"]['ipDataPlaneLearning']
            vrf_result.append((tenant, vrf, prference, direction, dbenforce, ipdata))
        vrf_result.sort(key=lambda x: x[0])

        return vrf_result

    def aci_bd_parser(self):
        bd_result = []
        pattern = r"tn-([A-Za-z0-9_]+)"
        for item in self.bd_to_vrf:
            dn = item["fvBD"]["attributes"]['dn']
            match = re.search(pattern, dn)
            info = match.groups()
            tenant = info[0]
            bd = item["fvBD"]["attributes"]['name']
            type0 = item["fvBD"]["attributes"]['type']
            hostBaseRouting = item["fvBD"]["attributes"]['hostBaseRouting']
            vrf = item["fvBD"]["children"][0]["fvRsCtx"]["attributes"]['tnFvCtxName']
            unkMacUcastAct = item["fvBD"]["attributes"]["unkMacUcastAct"]
            multiDstPktAct = item["fvBD"]["attributes"]["multiDstPktAct"]
            unicastRoute = item["fvBD"]["attributes"]['unicastRoute']
            arpFlood = item["fvBD"]["attributes"]['arpFlood']
            ipLearning = item["fvBD"]["attributes"]['ipLearning']
            mac = item["fvBD"]["attributes"]['mac']
            for item2 in item["fvBD"]['children']:
                if 'fvSubnet' in item2:
                    subnet = item["fvBD"]["children"][1]["fvSubnet"]["attributes"]['ip']
                else:
                    subnet = 'N/A'
            limitIplearnToSubnets = item["fvBD"]["attributes"]["limitIplearnToSubnets"]
            if "" == item['fvBD']['attributes']['epMoveDetectMode']:
                epMoveDetectMode = "no"
            else:
                epMoveDetectMode = item["fvBD"]["attributes"]["epMoveDetectMode"]
            for item3 in item['fvBD']['children']:
                if 'fvSubnet' in item3:
                    ipDPLearning = item["fvBD"]["children"][1]["fvSubnet"][
                        "attributes"
                    ]["ipDPLearning"]
                else:
                    ipDPLearning = 'N/A'
            bd_result.append((tenant, bd, type0, hostBaseRouting, vrf, unkMacUcastAct, multiDstPktAct, unicastRoute,arpFlood, ipLearning, mac, subnet, limitIplearnToSubnets, epMoveDetectMode,ipDPLearning))
            
        bd_result.sort(key=lambda x: x[0])
        
        return bd_result
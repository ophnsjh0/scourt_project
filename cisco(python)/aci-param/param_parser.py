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
                
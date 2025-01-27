import json
from tools import *

with open("new_intends.json", "r") as file:
    topology = json.load(file)

subnet_dict = give_subnet_number(topology)
print(subnet_dict)

print("\n")

subnet_interconnexion_dict = give_subnet_interconnexion(topology, subnet_dict)
print(subnet_interconnexion_dict)

print("\n")

for AS in topology :
    for router in topology[AS]['routers'] :
        
        if is_border_router(router, topology, AS):
    
            for AS_neighbor in topology[AS]["neighbor"]:
                for neighborRouter in topology[AS]["neighbor"][AS_neighbor]:
                    if neighborRouter == router:
                        for neighborRouter2 in topology[AS]["neighbor"][AS_neighbor][neighborRouter]:
                            print(get_subnet_interconnexion(AS, subnet_interconnexion_dict, router, neighborRouter2))


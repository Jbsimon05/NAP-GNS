import json
import time

from addresses import create_base_cfg, create_loopback_interface, create_interfaces
from protocols import activate_protocols

base_config = [
    "version 15.2",
    "service timestamps debug datetime msec",
    "service timestamps log datetime msec",
    "boot-start-marker",
    "boot-end-marker",
    "no aaa new-model",
    "no ip icmp rate-limit unreachable",
    "ip cef",
    "no ip domain lookup",
    "ipv6 unicast-routing",
    "ipv6 cef",
    "multilink bundle-name authenticated",
    "ip tcp synwait-time 5",
    "ip forward-protocol nd",
    "no ip http server",
    "no ip http secure-server",
    "control-plane",
    "line con 0",
    " exec-timeout 0 0",
    " privilege level 15",
    " logging synchronous",
    " stopbits 1",
    "line aux 0",
    " exec-timeout 0 0",
    " privilege level 15",
    " logging synchronous",
    " stopbits 1",
    "line vty 0 4",
    " login",
    "end"
]

def main(topology) :
    for AS in topology :
        for router in topology[AS]['routers'] :
            # config file vierge
            create_base_cfg(base_config, router)

            # interfaces Loopback0
            create_loopback_interface(router)

            # adressage ipv6
            create_interfaces(router, topology, AS)

            # RIP + OSPF + BGP
            activate_protocols(AS, router, topology)

if __name__ == "__main__":
    with open("intends.json", "r") as file:
        #var topo à partir de json
        topology = json.load(file)
    start = time.time()
    main(topology)
    end = time.time()
    print("Temps d'exécution total :", end - start)

# exécuter move_files en changeant le chemin d'accès

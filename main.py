import json
import time
import os

from addresses import create_base_cfg, create_loopback_interface, create_interfaces
# from protocols import activate_protocols
from move_files import move_files


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
            # Creates the basic config file
            create_base_cfg(base_config, router)

            # Creates the loopback interfaces in the config file
            create_loopback_interface(router)

            # Creates the IP addresses on the intefaces of the routers
            create_interfaces(router, topology, AS)

            # Activates RIP or OSPF on the router (soon BGP)
            # activate_protocols(AS, router, topology)


    move_files()

if __name__ == "__main__" :
    start = time.time()
    with open("new_intends.json", 'r') as file :
        topology = json.load(file)
    main(topology)
    end = time.time()
    print("Execution time : ", end-start)

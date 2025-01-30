from tools import insert_line, find_index, is_border_router

def activate_protocols(AS : str, router : str, topology : dict) -> None :
    """ 
    For a given router, activate RIP or OSPF
    Then activate BGP
    """
    # Creation of a router ID (unique for each router)
    router_ID = give_ID(router)

    # Activate RIP or OSPF
    if is_rip(topology, AS) :
        activate_rip(router, topology, AS)
    elif is_ospf(topology, AS) :
        activate_ospf(router, topology, AS, router_ID)

    # Activate BGP
    #activate_bgp(...)




def give_ID(router : str) -> str:
    """
    For a given router, give his ID

    Exemple : R1 -> 1.1.1.1
              R13 -> 13.13.13.13
    """
    # Get the number of the router
    x = router[1:]
    # Return it 
    return f"{x}.{x}.{x}.{x}"




def is_rip(topology : dict, AS : str) -> bool :
    """
    Return True if RIP must be activated, else False
    """
    return topology[AS]['protocol'] == "RIP"




def activate_rip(router : str, topology : dict, AS : str) -> None :
    """
    Activates RIP on the given router for all its interfaces
    """
    # Enableling RIP
    index_line = find_index(router, "no ip http secure-server\n")
    insert_line(router, index_line, f"ipv6 router rip process\n redistribute connected\n")

    # Activates RIP on all the interfaces
    for interface in topology[AS]['routers'][router].values() :
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_line(router, index_line, f" ipv6 rip process enable\n")




def is_ospf(topology : dict, AS : str) -> bool :
    """
    Return True if RIP must be activated, else False
    """
    return topology[AS]['protocol'] == "OSPF"




def activate_ospf(router: str, topology: dict, AS: str, router_ID: str) -> None :
    """
    Activates OSPF on the given router for all its interfaces
    """
    # Enable OSPF and set the router ID
    index_line = find_index(router, "no ip http secure-server\n")
    insert_line(router, index_line, f"ipv6 router ospf 1\n router-id {router_ID}\n")

    # Activates OSPF on all the interfaces
    for interface in topology[AS]['routers'][router].values():
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_line(router, index_line, f" ipv6 ospf 1 area 0\n")

    """
    # If the router is a border router on an interface : make this interface passive to avoid packet pollution
    if is_border_router(router, topology, AS) :
        index_line = find_index(router, "ip forward-protocol nd\n")
        insert_line(router, index_line, "router ospf 1\n")
        index_line = find_index(router, f" router-id {router_ID}\n")
        for AS_neighbor in topology[AS]["neighbor"]:
            if router in topology[AS]["neighbor"][AS_neighbor].keys():
                for interface in topology[AS]["neighbor"][AS_neighbor][router].values():
                    insert_line(router, index_line, f" passive-interface {interface}\n")
    """
                    
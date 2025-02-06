from tools import insert_line, find_index, is_border_router, generate_addresses_dict


def activate_protocols(AS: str, router: str, topology: dict) -> None:
    """
    For a given router, activate RIP or OSPF, then activate BGP.
    Args:
        AS (str): The AS identifier.
        router (str): The router identifier.
        topology (dict): The network topology.
    """
    # Creation of a router ID (unique for each router)
    router_ID = give_ID(router)
    # Activate RIP or OSPF
    if is_rip(topology, AS):
        activate_rip(router, topology, AS)
    elif is_ospf(topology, AS):
        activate_ospf(router, topology, AS, router_ID)
    # Activate BGP
    activate_bgp(router, topology, AS)

def give_ID(router: str) -> str:
    """
    For a given router, give its ID.
    Args:
        router (str): The router identifier.
    Returns:
        str: The router ID.
    Example:
        R1 -> 1.1.1.1
        R13 -> 13.13.13.13
    """
    # Get the number of the router
    x = router[1:]
    # Return it
    return f"{x}.{x}.{x}.{x}"

def is_rip(topology: dict, AS: str) -> bool:
    """
    Return True if RIP must be activated, else False.
    Args:
        topology (dict): The network topology.
        AS (str): The AS identifier.
    Returns:
        bool: True if RIP must be activated, False otherwise.
    """
    return topology[AS]['protocol'] == "RIP"

def activate_rip(router: str, topology: dict, AS: str) -> None:
    """
    Activates RIP on the given router for all its interfaces.
    Args:
        router (str): The router identifier.
        topology (dict): The network topology.
        AS (str): The AS identifier.
    """
    # Enabling RIP
    index_line = find_index(router, "no ip http secure-server\n")
    router_ID = give_ID(router)
    insert_line(router, index_line, f"ipv6 router rip process\n router-id {router_ID}\n redistribute connected\n")
    # Activates RIP on all the interfaces
    for interface in topology[AS]['routers'][router].values():
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_line(router, index_line, f" ipv6 rip process enable\n")
    # Activates RIP on the loopback interface
    index_line = find_index(router, "interface Loopback0\n") + 3
    insert_line(router, index_line, f" ipv6 rip process enable\n")

def is_ospf(topology: dict, AS: str) -> bool:
    """
    Return True if OSPF must be activated, else False.
    Args:
        topology (dict): The network topology.
        AS (str): The AS identifier.
    Returns:
        bool: True if OSPF must be activated, False otherwise.
    """
    return topology[AS]['protocol'] == "OSPF"

def activate_ospf(router: str, topology: dict, AS: str, router_ID: str) -> None:
    """
    Activates OSPF on the given router for all its interfaces.
    Args:
        router (str): The router identifier.
        topology (dict): The network topology.
        AS (str): The AS identifier.
        router_ID (str): The router ID.
    """
    # Enable OSPF and set the router ID
    index_line = find_index(router, "no ip http secure-server\n")
    insert_line(router, index_line, f"ipv6 router ospf 1\n router-id {router_ID}\n redistribute connected\n 
                \n")
    # Activates OSPF on all the interfaces
    for interface in topology[AS]['routers'][router].values():
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_line(router, index_line, f" ipv6 ospf 1 area 0\n")
    # If the router is a border router on an interface: make this interface passive to avoid packet pollution
    if is_border_router(router, topology, AS):
        index_line = find_index(router, "ip forward-protocol nd\n")
        insert_line(router, index_line, "router ospf 1\n")
        index_line = find_index(router, f" router-id {router_ID}\n")
        for AS_neighbor in topology[AS]["neighbor"]:
            if router in topology[AS]["neighbor"][AS_neighbor].keys():
                for interface in topology[AS]["neighbor"][AS_neighbor][router].values():
                    insert_line(router, index_line, f" passive-interface {interface}\n")
    # Activates OSPF on the loopback interface
    index_line = find_index(router, "interface Loopback0\n") + 3
    insert_line(router, index_line, f" ipv6 ospf 1 area 0\n")

def activate_bgp(routeur: str, topology: dict, AS: str) -> None:
    """
    Activates BGP on the given router using the Loopback addresses of its neighbors.
    Args:
        routeur (str): The router identifier.
        topology (dict): The network topology.
        AS (str): The AS identifier.
    """
    # Generate the addresses dictionary
    addresses_dict = generate_addresses_dict(topology)
    # Find the line to insert BGP configuration
    index_line = find_index(routeur, "ip forward-protocol nd\n") - 1
    # Insert BGP configuration
    insert_line(routeur, index_line,
                f"router bgp 10{AS[-1]}\n"
                f" bgp router-id {give_ID(routeur)}\n"
                f" bgp log-neighbor-changes\n"
                f" no bgp default ipv4-unicast\n")
    index_line += 4
    # Add neighbors for all routers in the same AS
    for router_in_as in topology[AS]['routers']:
        if router_in_as != routeur:
            neighbor_loopback = f"2001::{router_in_as[1:]}"
            insert_line(routeur, index_line, f" neighbor {neighbor_loopback} remote-as 10{AS[-1]}\n")
            insert_line(routeur, index_line + 1, f" neighbor {neighbor_loopback} update-source Loopback0\n")
            index_line += 2
    # Add neighbors for BGP for border routers
    for neighbor_info in addresses_dict[routeur]:
        for neighbor, details in neighbor_info.items():
            interface, ipv6_address, neighbor_AS = details
            if AS != neighbor_AS:
                # Use the link address between the two routers
                link_address = ipv6_address.split("::")[0] + "::" + ("2" if ipv6_address.endswith("::1/64") else "1")
                insert_line(routeur, index_line, f" neighbor {link_address} remote-as 10{neighbor_AS[-1]}\n")
                index_line += 1
    # Add address-family for IPv6
    insert_line(routeur, index_line, " address-family ipv4\n exit-address-family\n address-family ipv6\n  network 2001::/128\n")
    index_line += 4
    # Add network statements and activate neighbors in address-family
    for neighbor_info in addresses_dict[routeur]:
        for neighbor, details in neighbor_info.items():
            interface, ipv6_address, neighbor_AS = details
            # Format the network address
            network_address = ipv6_address.split("::")[0] + "::/64"
            insert_line(routeur, index_line, f"  network {network_address}\n")
            index_line += 1
            if AS == neighbor_AS:
                # Use the Loopback address of the neighbor
                neighbor_loopback = f"2001::{neighbor[1:]}"
                insert_line(routeur, index_line, f"  neighbor {neighbor_loopback} activate\n")
                index_line += 1
            else:
                # Use the link address between the two routers
                link_address = ipv6_address.split("::")[0] + "::" + ("2" if ipv6_address.endswith("::1/64") else "1")
                insert_line(routeur, index_line, f"  neighbor {link_address} activate\n")
                index_line += 1
    # Activate neighbors in address-family for all routers in the same AS
    for router_in_as in topology[AS]['routers']:
        if router_in_as != routeur:
            neighbor_loopback = f"2001::{router_in_as[1:]}"
            insert_line(routeur, index_line, f"  neighbor {neighbor_loopback} activate\n")
            index_line += 1
    insert_line(routeur, index_line, " exit-address-family\n")
from tools import insert_line, find_index, is_border_router, give_subnet_dict, give_subnet_interconnexion, get_subnet_interconnexion



def create_base_cfg(base_config : list, router : str) -> None :
    """
    Creates the base config file named iX_startup-config.cfg
    With X the number/name of the router

    The file contains all the lines form the base_config list plus the hostname of the router (= number/name)
    """
    # Writes the base_config in the config file
    with open(f'i{router[1:]}_startup-config.cfg', 'w') as file :
        for entry in base_config :
            file.write(entry + '\n')
    # Writes the hostname in the config file
    insert_line(router, 3, f"hostname {router}\n")   



def create_loopback_interface(router : str) -> None :
    """ 
    Insert the loopback lines at the right place in the config file of a given router
    """
    # Finds the index of where to insert the loopback part
    index_line = find_index(router, "ip tcp synwait-time 5\n")
    #Insert the loopback part 
    insert_line(router, index_line, f"interface Loopback0\n no ip address\n ipv6 address 2001::{router[1:]}/128\n ipv6 enable\n")



def create_interfaces(router: str, topology: dict, AS: str) -> None:
    """
    Generate the interfaces with the correct IPv6 addresses for each router of each AS 
    
    Example: 
        interface GigabitEthernet1/0
        no ip address
        negotiation auto
        ipv6 address 2001:192:168:11::1/64
        ipv6 enable
    """
    # Creates the subnet_dict
    subnet_dict = give_subnet_dict(topology)

    # Finds the line where to insert the interface
    index_line = find_index(router, line="ip tcp synwait-time 5\n")

    # Iterate over each neighbor in the AS topology
    for neighbor in topology[AS]['routers'][router].keys():
        # To ensure it's in the correct order
        if router[1:] < neighbor[1:]:
            subnet_index = subnet_dict[AS][(router, neighbor)]
            router_index = 1
        else:
            subnet_index = subnet_dict[AS][(neighbor, router)]
            router_index = 2
        
        # Insert the lines in the config files for the interface
        insert_line(router, index_line,
            f"interface {topology[AS]['routers'][router][neighbor]}\n"  # Interface name
            f" no ip address\n"  # Disable IPv4 addressing
            f" negotiation auto\n"  # Enable automatic negotiation for the interface
            f" ipv6 address {topology[AS]['address']}{subnet_index}::{router_index}{topology[AS]['subnet_mask']}\n"  # Assign an IPv6 address
            f" ipv6 enable\n"  # Enable IPv6 on the interface
        )

        # Increment the index line to ensure the next configuration is inserted at the correct position
        index_line += 5
    
    
    if is_border_router(router, topology, AS):

        index_line = find_index(router, "ip forward-protocol nd\n") - 1
        subnet_interconnexion_dict = give_subnet_interconnexion(topology, subnet_dict)

        for AS_neighbor in topology[AS]["neighbor"]:
            for neighborRouter in topology[AS]["neighbor"][AS_neighbor]:
                if neighborRouter == router:
                    for neighborRouter2 in topology[AS]["neighbor"][AS_neighbor][neighborRouter]:
                        insert_line(router, index_line,
                                        f"interface {topology[AS]['neighbor'][AS_neighbor][neighborRouter][neighborRouter2]}\n"
                                        f" no ip address\n"
                                        f" negotiation auto\n" 
                                        f" ipv6 address {topology[AS]['address'][:-1]}{get_subnet_interconnexion(AS, subnet_interconnexion_dict, router, neighborRouter2)}{topology[AS]['subnet_mask']}\n" 
                                        f" ipv6 enable\n"
                                        )
                        index_line += 5
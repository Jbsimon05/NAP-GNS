from tools import insert_line, find_index

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




def give_subnet_number(topology : dict) -> dict :
    """ 
    Creates a dict associating a unique number to every physical link in the network

    Exemaple : {'AS_1': {('R1', 'R2'): 1, ('R1', 'R3'): 2, ... }
    """
    subnet_dict = {}
    # Iterate over each AS
    for AS in topology :
        subnet_dict[AS] = {}
        subnet_number = 1
        # Iterate over each router of the current AS
        for router in topology[AS]['routers'] :
            # Iterate over each neighbor of the current router
            for neighbor in topology[AS]['routers'][router] :
                # To avoid duplicates, ensure the router with the smaller numeric suffix comes first
                if router[1:] < neighbor[1:] :
                    subnet_dict[AS][(router, neighbor)] = subnet_number
                    subnet_number += 1
    return subnet_dict




def create_interfaces(router : str, topology : dict, AS : str) -> None :
    """
    Generate the interfaces with the correct IPv6 addresses for each routrer of each AS 
    
    Exemaple : 
        interface GigabitEthernet1/0
        no ip address
        negotiation auto
        ipv6 address 2001:192:168:11::1/64
        ipv6 enable
    """
    #Creates the subnet_dict
    subnet_dict = give_subnet_number(topology)

    #Finds the line where to insert the interface
    index_line = find_index(router, line="ip tcp synwait-time 5\n")

    #Iterate over ...
    for neighbor in topology[AS]['routers'][router].keys() :
        # To ensure it's in the correct order
        if router[1:] < neighbor[1:] :
            subnet_index = subnet_dict[AS][(router, neighbor)]
            router_index = 1
        else :
            subnet_index = subnet_dict[AS][(neighbor, router)]
            router_index = 2
        
        #Insert the lines in the config files
        insert_line(router, index_line,
            f"interface {topology[AS]['routers'][router][neighbor]}\n"  # Interface name
            f" no ip address\n"  # Disable IPv4 addressing
            f" negotiation auto\n"  # Enable automatic negotiation for the interface
            f" ipv6 address {topology[AS]['address']}{subnet_index}::{router_index}{topology[AS]['subnet_mask']}\n"  # Assign an IPv6 address
            f" ipv6 enable\n"  # Enable IPv6 on the interface
        )

        # Increment the index line to ensure the next configuration is inserted at the correct position
        index_line += 5
def insert_line(router : str, index_line : int, data : str) -> None :
    """
    For a given router, insert the data at indexline in its config file
    """
    # Get the lines in the file and insert the new one
    with open(f"i{router[1:]}_startup-config.cfg", 'r') as file :
        lines = file.readlines()
        lines.insert(index_line, data)
    # Writes the updated list in the file
    with open(f"i{router[1::]}_startup-config.cfg", 'w') as file :
        file.writelines(lines)


def find_index(router : str, line : str) -> int :
    """ 
    For a given router, finds the index of a given line in its config file
    """
    current_index = 1
    with open(f'i{router[1:]}_startup-config.cfg', 'r') as file:
        # Browses the lines to find the wanted one
        l = file.readline()
        while l != line:
            l = file.readline()
            current_index += 1
    return current_index


def give_subnet_dict(topology : dict) -> dict :
    """ 
    Creates a dict associating a unique number to every physical link in the network

    Example : {'AS_1': {('R1', 'R2'): 1, ('R1', 'R3'): 2, ... }
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


def is_border_router(routeur : str, topology : dict, AS : str) -> bool :
    """
    Return whether a given routeur is a border router of his AS
    """
    state = False
    for AS in topology :
        for AS_neighbor in topology[AS]['neighbor'] : 
            if routeur in topology[AS]['neighbor'][AS_neighbor].keys() :
                state = True 
    return state


def last_entries_subnet(subnet_dict : dict) -> int :
    """
    Find and return the last subnet value used 
    """
    last_entry = dict()
    for AS in subnet_dict:
        last_entry[AS] = list(subnet_dict[AS].values())[-1]
    return last_entry


def give_subnet_interconnexion(topology : dict, subnet_dict : dict) -> dict :
    """
    Generates a dict of subnets for the inter-AS connexions
    """
    # Create necessary dict
    subnet_interconnexion_dict = dict()
    last_entries = last_entries_subnet(subnet_dict)
    for AS in topology:
        subnet_interconnexion_dict[AS] = dict()
    
    # Iterate over each AS
    for AS in topology:
        # Iterate over each AS neighbor
        for AS_neighbor in topology[AS]['neighbor']:
            # Iterate over each border Router
            for router1 in topology[AS]['neighbor'][AS_neighbor]:
                # Iterate over each neighbor Router
                for router2 in topology[AS]['neighbor'][AS_neighbor][router1]:
                    # Check externality of the link
                    if (router1, router2) not in subnet_interconnexion_dict[AS].keys() and (router2, router1) not in subnet_interconnexion_dict[AS].keys():
                        # Create the end of the address of each externnal interface of borderRouters (ex. 111::1 -> AS 1, link 11, router 1)
                        if AS < AS_neighbor:
                            subnet_interconnexion_dict[AS][(router1, router2)] = str(int(AS[3:])) + str((last_entries[AS] + 1)) + "::1"
                            subnet_interconnexion_dict[AS_neighbor][(router2, router1)] = str(int(AS[3:])) + str((last_entries[AS] + 1)) + "::2"
                        else:
                            subnet_interconnexion_dict[AS][(router1, router2)] = str(int(AS_neighbor[3:])) + str((last_entries[AS] + 1)) + "::1"
                            subnet_interconnexion_dict[AS_neighbor][(router2, router1)] = str(int(AS_neighbor[3:])) + str((last_entries[AS] + 1)) + "::2"
                        last_entries[AS] += 1
    return subnet_interconnexion_dict


def get_subnet_interconnexion(AS : str, subnet_interconnexion_dict : dict, routeur1 : str, routeur2 : str) -> str :
    """
    Retrieve the IPv6 address of an interconnection subnet between two given routers
    """
    return subnet_interconnexion_dict[AS][(routeur1, routeur2)] or subnet_interconnexion_dict[AS][(routeur2, routeur1)]


def generate_addresses_dict(topology: dict) -> dict:
    """
    Generates a dictionary with neighbors, interfaces, IP addresses, and AS for each router.
    
    Output format:
    {
        "R1": [{"R2": ["interface", "ipv6 address", "AS"]}, {"R3": ["interface", "ipv6 address", "AS"]}, ...],
        "R2": [{"R1": ["interface", "ipv6 address", "AS"]}, {"R4": ["interface", "ipv6 address", "AS"]}, ...],
        ...
    }
    """
    router_neighbors = {}

    # Creates the subnet_dict
    subnet_dict = give_subnet_dict(topology)
    subnet_interconnexion_dict = give_subnet_interconnexion(topology, subnet_dict)

    # Iterate over each AS
    for AS in topology:
        # Iterate over each router in the current AS
        for router in topology[AS]['routers']:
            if router not in router_neighbors:
                router_neighbors[router] = []

            # Iterate over each neighbor of the current router
            for neighbor, interface in topology[AS]['routers'][router].items():
                # To ensure it's in the correct order
                if router[1:] < neighbor[1:]:
                    subnet_index = subnet_dict[AS][(router, neighbor)]
                    router_index = 1
                else:
                    subnet_index = subnet_dict[AS][(neighbor, router)]
                    router_index = 2
                ipv6_address = f"{topology[AS]['address']}{subnet_index}::{router_index}{topology[AS]['subnet_mask']}"
                router_neighbors[router].append({neighbor: [interface, ipv6_address, AS]})

    # Handle inter-AS connections
    for AS in topology:
        for AS_neighbor in topology[AS]['neighbor']:
            for router1 in topology[AS]['neighbor'][AS_neighbor]:
                for router2, interface in topology[AS]['neighbor'][AS_neighbor][router1].items():
                    if router1 not in router_neighbors:
                        router_neighbors[router1] = []
                    if router2 not in router_neighbors:
                        router_neighbors[router2] = []

                    # Check if the connection already exists to avoid duplication
                    if not any(neighbor.get(router2) for neighbor in router_neighbors[router1]):
                        if int(AS[3:]) < int(AS_neighbor[3:]):
                            ipv6_address1 = f"{topology[AS]['address'][:-1]}{get_subnet_interconnexion(AS, subnet_interconnexion_dict, router1, router2)}{topology[AS]['subnet_mask']}"
                            ipv6_address2 = f"{topology[AS]['address'][:-1]}{get_subnet_interconnexion(AS_neighbor, subnet_interconnexion_dict, router2, router1)}{topology[AS]['subnet_mask']}"
                        else:
                            ipv6_address1 = f"{topology[AS]['address'][:-1]}{get_subnet_interconnexion(AS_neighbor, subnet_interconnexion_dict, router2, router1)}{topology[AS]['subnet_mask']}"
                            ipv6_address2 = f"{topology[AS]['address'][:-1]}{get_subnet_interconnexion(AS, subnet_interconnexion_dict, router1, router2)}{topology[AS]['subnet_mask']}"

                        router_neighbors[router1].append({router2: [interface, ipv6_address1, AS_neighbor]})
                        router_neighbors[router2].append({router1: [interface, ipv6_address2, AS]})

    return router_neighbors
def activate_bgp(routeur: str, topology: dict, AS: str) -> None:
    """
    Activates BGP on the given router using the Loopback addresses of its neighbors
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

    # Add neighbors for BGP
    for neighbor_info in addresses_dict[routeur]:
        for neighbor, details in neighbor_info.items():
            interface, ipv6_address, neighbor_AS = details
            if AS == neighbor_AS:
                # Use the Loopback address of the neighbor
                neighbor_loopback = f"2001::{neighbor[1:]}"
                insert_line(routeur, index_line, f" neighbor {neighbor_loopback} remote-as 10{neighbor_AS[-1]}\n")
                insert_line(routeur, index_line + 1, f" neighbor {neighbor_loopback} update-source Loopback0\n")
                index_line += 2
            else:
                # Use the link address between the two routers
                link_address = ipv6_address.split("::")[0] + "::" + ("2" if ipv6_address.endswith("::1/64") else "1")
                insert_line(routeur, index_line, f" neighbor {link_address} remote-as 10{neighbor_AS[-1]}\n")
                index_line += 1

    # Add address-family for IPv6
    insert_line(routeur, index_line, " address-family ipv4\n exit-address-family\n address-family ipv6\n  network 2001::/128\n")
    index_line += 4

    # Activate neighbors in address-family and add network statements
    neighborConf = ""
    networkConf = ""
    index_sum = 0
    for neighbor_info in addresses_dict[routeur]:
        for neighbor, details in neighbor_info.items():
            interface, ipv6_address, neighbor_AS = details
            if AS == neighbor_AS:
                # Use the Loopback address of the neighbor
                neighbor_loopback = f"2001::{neighbor[1:]}"
                neighborConf += f"  neighbor {neighbor_loopback} activate\n"
            else:
                # Use the link address between the two routers
                link_address = ipv6_address.split("::")[0] + "::" + ("2" if ipv6_address.endswith("::1/64") else "1")
                neighborConf += f"  neighbor {link_address} activate\n"
            # Format the network address
            network_address = ipv6_address.split("::")[0] + "::/64"
            networkConf += f"  network {network_address}\n"
            index_sum += 1
    insert_line(routeur, index_line, networkConf)
    index_line += index_sum
    insert_line(routeur, index_line, neighborConf)
    index_line += index_sum

    insert_line(routeur, index_line, " exit-address-family\n")
import json

def generate_config(router, as_config):
    config = []
    config.append(f"hostname {router['name']}")
    config.append("!")

    # Loopback interface
    config.append(f"interface Loopback0")
    config.append(f" ipv6 address {router['loopback']}")
    config.append("!")

    # Physical interfaces
    for interface in router['interfaces']:
        config.append(f"interface {interface['name']}")
        config.append(f" ipv6 address {interface['ip']}")
        config.append("!")

    # IGP configuration
    if as_config['IGP'] == "RIP":
        config.append("ipv6 unicast-routing")
        config.append("ipv6 router rip RIP_PROCESS")
        for interface in router['interfaces']:
            config.append(f" interface {interface['name']}")
        config.append("!")
    elif as_config['IGP'] == "OSPF":
        config.append("ipv6 unicast-routing")
        config.append("ipv6 router ospf 1")
        config.append(" router-id 1.1.1.1")
        for interface in router['interfaces']:
            config.append(f" interface {interface['name']}")
            config.append("  area 0")
        config.append("!")

    # BGP configuration
    config.append(f"router bgp {router['bgp']['asn']}")
    config.append(" bgp log-neighbor-changes")
    config.append(f" neighbor {router['bgp']['neighbors'][0]['ip']} remote-as {router['bgp']['neighbors'][0]['remote_as']}")
    config.append("!")

    return "\n".join(config)

def main():
    with open('config.json', 'r') as f:
        data = json.load(f)

    for as_name, as_config in data.items():
        for router in as_config['routers']:
            config = generate_config(router, as_config)
            with open(f"{router['name']}_config.txt", 'w') as f:
                f.write(config)

if __name__ == "__main__":
    main()

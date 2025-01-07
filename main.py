import json
import paramiko

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
    for neighbor in router['bgp']['neighbors']:
        config.append(f" neighbor {neighbor['ip']} remote-as {neighbor['remote_as']}")
    config.append("!")

    return "\n".join(config)

def deploy_config_to_gns3(router_name, config, hostname, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)

    commands = config.split("\n")
    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()

    ssh.close()

def main():
    with open('config.json', 'r') as f:
        data = json.load(f)

    gns3_host = "localhost"
    gns3_port = 22
    gns3_username = "admin"
    gns3_password = "admin"

    for as_name, as_config in data.items():
        for router in as_config['routers']:
            config = generate_config(router, as_config)
            deploy_config_to_gns3(router['name'], config, gns3_host, gns3_port, gns3_username, gns3_password)

if __name__ == "__main__":
    main()

import json
import paramiko
import socket

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
        config.append(" no shutdown")
        config.append("!")

    # IGP configuration
    if as_config['IGP'] == "RIP":
        config.append("ipv6 unicast-routing")
        config.append("ipv6 router rip NAME_OF_PROCESS")
        for interface in router['interfaces']:
            config.append(f" network {interface['ip'].split('/')[0]}")
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
        config.append(f" neighbor {neighbor['ip'].split('/')[0]} remote-as {neighbor['remote_as']}")
    config.append("!")

    return "\n".join(config)

def deploy_config_to_gns3(router_name, config, hostname, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)

        # Enter enable mode
        stdin, stdout, stderr = ssh.exec_command("enable")
        stdout.channel.recv_exit_status()

        # Enter global configuration mode
        stdin, stdout, stderr = ssh.exec_command("configure terminal")
        stdout.channel.recv_exit_status()

        # Apply configuration
        commands = config.split("\n")
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            stdout.channel.recv_exit_status()

        # Exit configuration mode and save
        stdin, stdout, stderr = ssh.exec_command("end")
        stdout.channel.recv_exit_status()
        stdin, stdout, stderr = ssh.exec_command("write memory")
        stdout.channel.recv_exit_status()

        ssh.close()
        print(f"Configuration deployed successfully for {router_name}")

    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(f"Unable to connect to {hostname} on port {port}: {e}")
    except paramiko.ssh_exception.AuthenticationException as e:
        print(f"Authentication failed for {hostname}: {e}")
    except paramiko.ssh_exception.SSHException as e:
        print(f"SSH error occurred: {e}")
    except socket.error as e:
        print(f"Socket error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    with open('config.json', 'r') as f:
        data = json.load(f)

    gns3_host = "::1"  # Utilisation de l'adresse IPv6 localhost
    gns3_port = 3080
    gns3_username = "admin"
    gns3_password = "admin"

    for as_name, as_config in data.items():
        for router in as_config['routers']:
            config = generate_config(router, as_config)
            deploy_config_to_gns3(router['name'], config, gns3_host, gns3_port, gns3_username, gns3_password)

if __name__ == "__main__":
    main()

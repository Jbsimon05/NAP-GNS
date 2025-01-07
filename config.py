from gns3fy import Gns3Connector, Project, Node

# Constants for GNS3 server
GNS3_SERVER_URL = "http://localhost:3080"  # URL de l'instance GNS3
PROJECT_NAME = "Network_Automation_Project"

# Addressing and configuration data
ADDRESS_PLAN = {
    "AS_X": {
        "loopback_range": "10.1.1.0/24",
        "physical_range": "192.168.1.0/24",
        "protocol": "RIP",
    },
    "AS_Y": {
        "loopback_range": "10.2.1.0/24",
        "physical_range": "192.168.2.0/24",
        "protocol": "OSPF",
    }
}

# Functions to handle network configuration
def connect_to_gns3():
    """Connects to the GNS3 server."""
    return Gns3Connector(GNS3_SERVER_URL)

def get_or_create_project(connector):
    """Gets or creates the specified project."""
    project = Project(name=PROJECT_NAME, connector=connector)
    project.get()  # Tries to fetch the project
    if not project.project_id:  # If project does not exist, create it
        project.create()
    return project

def setup_nodes(project):
    """Sets up routers and their initial configurations."""
    for as_name, config in ADDRESS_PLAN.items():
        for i in range(2):  # Example: 2 routers per AS
            node_name = f"{as_name}_Router{i+1}"
            node = Node(name=node_name, project=project)
            node.create(template="RouterTemplate")
            configure_router(node, config, i)

def configure_router(node, config, index):
    """Applies initial configurations to a router."""
    loopback_ip = f"{config['loopback_range'].split('.')[0]}.{index+1}/32"
    print(f"Configuring {node.name} with loopback IP {loopback_ip}")
    config_commands = [
        f"interface loopback0",
        f"ip address {loopback_ip}",
        "no shutdown",
        f"router {config['protocol'].lower()}",
        "network 0.0.0.0"
    ]
    # Apply the commands (example only; this requires CLI interaction in real use)
    for cmd in config_commands:
        print(f"{node.name} >> {cmd}")

# BGP configuration
def configure_bgp(project):
    """Configures BGP for inter-AS communication."""
    print("Configuring BGP...")
    for as_name in ADDRESS_PLAN.keys():
        for i in range(2):
            router_name = f"{as_name}_Router{i+1}"
            print(f"{router_name} >> Configuring BGP settings")
            # Example commands (to be replaced with actual GNS3 interactions)
            bgp_commands = [
                "router bgp 65001",  # Replace with actual AS number
                "neighbor 10.1.1.2 remote-as 65002",  # Example neighbor
                "network 10.1.1.0 mask 255.255.255.0"
            ]
            for cmd in bgp_commands:
                print(f"{router_name} >> {cmd}")

# Main execution flow
def main():
    connector = connect_to_gns3()
    project = get_or_create_project(connector)
    setup_nodes(project)
    configure_bgp(project)

if __name__ == "__main__":
    main()

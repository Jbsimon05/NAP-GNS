import gns3fy
import telnetlib3
import asyncio

# Connect to the GNS3 server
gns3_server = gns3fy.Gns3Connector("http://localhost:3080")

# Load the project
project = gns3fy.Project(name="GNS_renew", connector=gns3_server)
project.get()
project.open()

# Retrieve all nodes from the project
nodes = {node.name: node for node in project.nodes}

# Define the IPv6 topology and configurations
topology_config = {
    "R1": {"g1/0": "2001:db8:1::1/64", "g2/0": "2001:db8:3::1/64"},
    "R2": {"g1/0": "2001:db8:1::2/64", "g3/0": "2001:db8:2::1/64"},
    "R3": {"g1/0": "2001:db8:3::2/64", "g2/0": "2001:db8:4::1/64"},
    "R4": {"g2/0": "2001:db8:2::2/64", "g3/0": "2001:db8:5::1/64", "f0/0": "2001:db8:6::1/64"},
    "R5": {"f0/0": "2001:db8:6::2/64", "g2/0": "2001:db8:7::1/64", "g3/0": "2001:db8:4::2/64"},
    "R6": {"g1/0": "2001:db8:5::2/64", "f0/0": "2001:db8:8::1/64"},
    "R7": {"f0/0": "2001:db8:8::2/64", "g2/0": "2001:db8:7::2/64"},
}

# Telnet settings
TELNET_HOST = "127.0.0.1"
TELNET_TIMEOUT = 5

async def configure_router_via_telnet(router_name, interfaces):
    # Get the router node
    node = nodes.get(router_name)
    if not node:
        print(f"Router {router_name} not found.")
        return

    # Get the Telnet port for the router
    telnet_port = node.properties.get("console")
    if not telnet_port:
        print(f"Router {router_name} does not have a Telnet console.")
        return

    print(f"Connecting to {router_name} on port {telnet_port}...")

    try:
        # Connect to the router via Telnet using telnetlib3
        async with telnetlib3.open_connection(
            host=TELNET_HOST, port=telnet_port, connect_minwait=1
        ) as conn:
            # Wait for the initial prompt
            await conn.read_very_eager()

            # Enter enable mode
            await conn.write("enable\n")
            await conn.read_until("Router#")

            # Enter configuration mode
            await conn.write("configure terminal\n")
            await conn.read_until("(config)#")

            # Apply configurations
            for interface, ipv6_address in interfaces.items():
                commands = [
                    f"interface {interface}",
                    f"ipv6 address {ipv6_address}",
                    "ipv6 enable",
                    "ipv6 rip GNS3 enable",
                ]
                for command in commands:
                    await conn.write(f"{command}\n")
                    await asyncio.sleep(0.5)
                await conn.write("exit\n")

            # Save the configuration
            await conn.write("write memory\n")
            await asyncio.sleep(2)

            # Exit configuration mode
            await conn.write("exit\n")
            print(f"Configuration applied to {router_name}.")

    except Exception as e:
        print(f"Error configuring {router_name}: {e}")

# Run all configurations asynchronously
async def main():
    tasks = [
        configure_router_via_telnet(router_name, interfaces)
        for router_name, interfaces in topology_config.items()
    ]
    await asyncio.gather(*tasks)

print("Starting router configuration...")
asyncio.run(main())
print("All configurations applied successfully.")
# NAP-GNS
3TC semestre 1 - Network Automation Project sous GNS

This project automates the configuration of network devices in a multi-AS (Autonomous System) topology using JSON-based intents and Python scripts. The network includes three ASes with distinct routing protocols (RIP and OSPF) and interconnectivity using BGP.

**Project Structure** - Address Plan

- AS X

  Loopback Range: 10.1.1.0/24

  Physical Range: 192.168.1.0/24

  Routing Protocol: RIP

- AS Y

  Loopback Range: 10.2.1.0/24

  Physical Range: 192.168.2.0/24

  Routing Protocol: OSPF

- Inter-AS Connectivity

  AS X to AS Y: eBGP

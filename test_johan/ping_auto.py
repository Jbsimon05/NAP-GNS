import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

base_config = [
    "version 15.2",
    "service timestamps debug datetime msec",
    "service timestamps log datetime msec",
    "boot-start-marker",
    "boot-end-marker",
    "no aaa new-model",
    "no ip icmp rate-limit unreachable",
    "ip cef",
    "no ip domain lookup",
    "ipv6 unicast-routing",
    "ipv6 cef",
    "multilink bundle-name authenticated",
    "ip tcp synwait-time 5",
    "ip forward-protocol nd",
    "no ip http server",
    "no ip http secure-server",
    "control-plane",
    "line con 0",
    " exec-timeout 0 0",
    " privilege level 15",
    " logging synchronous",
    " stopbits 1",
    "line aux 0",
    " exec-timeout 0 0",
    " privilege level 15",
    " logging synchronous",
    " stopbits 1",
    "line vty 0 4",
    " login",
    "end"]


def main(topology):
    with ThreadPoolExecutor() as executor:
        futures = []
        subnet_dict = give_subnet_number(topology)
        subnet_interconnexion_dict = give_subnet_interconnexion(topology, subnet_dict)
        for AS in topology:
            for router in topology[AS]['routers']:
                future = executor.submit(process_router, router, AS, subnet_dict[AS], subnet_interconnexion_dict[AS], topology)
                futures.append(future)

        for future in futures:
            future.result()


def process_router(router, AS, subnet_dict, subnet_interconnexion_dict, topology):
    create_base_cfg(router, base_config)
    create_loopback_interface(router, topology[AS])
    create_router_interfaces(router, AS, topology[AS], subnet_dict)
    activate_protocols(router, AS, topology[AS], subnet_interconnexion_dict,subnet_dict)


def insert_cfg_line(router, index_line, data):
    # insert une information 'data' à la ligne 'line'.
    with open(f'i{router[1:]}_startup-config.cfg', 'r') as file:
        lines = file.readlines()
        lines.insert(index_line, data)
    with open(f'i{router[1:]}_startup-config.cfg', 'w') as file:
        file.writelines(lines)


def create_base_cfg(router, base_config):
    # créer pour un routeur, son fichier cfg de base à partir d'une liste 'base config', et insert l'hostname.
    with open(f'i{router[1:]}_startup-config.cfg', 'w') as file:
        for entry in base_config:
            file.write(entry + '\n')
    insert_cfg_line(router, 3, f"hostname {router}\n")


def find_index(router, line):
    # Trouve l'indice correcte pour inserer une nouvelle ligne juste après la ligne 'line'.
    index_line = 1
    with open(f'i{router[1:]}_startup-config.cfg', 'r') as file:
        lines = file.readline()
        while lines != line:
            lines = file.readline()
            index_line += 1
    return index_line


def create_router_interfaces(router, AS, as_topology, subnet_dict):
    # insert dans le cfg du routeur toutes les ses interfaces et leurs ipv6 correspondantes.
    index_line = find_index(router, line="ip tcp synwait-time 5\n")

    for neighbor in as_topology['routers'][router].keys():
        if router[1:] < neighbor[1:]:
            subnet_index = subnet_dict[(router, neighbor)]
            router_index = 1
        else:
            subnet_index = subnet_dict[(neighbor, router)]
            router_index = 2

        insert_cfg_line(router, index_line,
                        f"interface {as_topology['routers'][router][neighbor]}\n no ip address\n negotiation auto\n ipv6 address {as_topology['address']}{subnet_index}::{router_index}{as_topology['subnet_mask']}\n ipv6 enable\n")
        index_line += 5

def give_subnet_number(as_topology):  # Crée le tableau des subnets pour tout le json
    subnet_dict = dict()
    for AS in as_topology:
        subnet_dict[AS] = dict()
        subnet_number = 1
        for router in as_topology[AS]['routers']:
            for neighbor in as_topology[AS]['routers'][router]:
                if router[1:] < neighbor[1:]:
                    subnet_dict[AS][(router, neighbor)] = subnet_number
                    subnet_number += 1
    return subnet_dict

def last_entries_subnet(subnet_dict):
    last_entry = dict()
    for AS in subnet_dict:
        last_entry[AS] = list(subnet_dict[AS].values())[-1]
    return last_entry

def give_subnet_interconnexion(topology, subnet_dict):
    """
    Génère un dictionnaire des sous-réseaux d'interconnexion entre routeurs dans différents AS.
    """
    subnet_interconnexion_dict = {}
    last_entries = {}

    for AS in topology:
        # Vérifiez que la clé AS est valide
        if not AS.startswith("AS") or not AS[2:].isdigit():
            raise ValueError(f"Clé AS invalide détectée : {AS}")
        
        # Initialisation pour cet AS
        subnet_interconnexion_dict[AS] = {}
        last_entries[AS] = 0

        if "neighbor" in topology[AS]:
            for neighbor_AS in topology[AS]["neighbor"]:
                # Vérifiez que le voisin est valide
                if not neighbor_AS.startswith("AS") or not neighbor_AS[2:].isdigit():
                    raise ValueError(f"Clé AS voisine invalide détectée : {neighbor_AS}")

                for router1 in topology[AS]["neighbor"][neighbor_AS]:
                    for router2 in topology[AS]["neighbor"][neighbor_AS][router1]:
                        # Génère un sous-réseau d'interconnexion unique
                        last_entries[AS] += 1
                        subnet_interconnexion_dict[AS][(router1, router2)] = (
                            str(int(AS[2:])) + str(last_entries[AS]) + "::1"
                        )
                        subnet_dict[(router1, router2)] = str(int(AS[2:])) + str(last_entries[AS])

    return subnet_interconnexion_dict

def is_rip(as_topology):
    # retourne True si RIP est à activer, False sinon.
    return True if as_topology["protocol"] == "RIP" else False

def is_ospf(as_topology):
    # retourne True si RIP est à activer, False sinon
    return True if as_topology["protocol"] == "OSPF" else False


def activate_protocols(router, AS, as_topology, subnet_interconnexion_dict,subnet_dict):
    # active tous les protocols d'un routeur.
    router_id = give_router_id(router)
    if is_ospf(as_topology):
        activate_ospf(router, as_topology, router_id)
    elif is_rip(as_topology):
        activate_rip(router, as_topology)
    activate_bgp(router, AS, as_topology, subnet_interconnexion_dict,subnet_dict)


def activate_ospf(router, as_topology, router_id):
    # active OSPF sur le routeur.
    index_line = find_index(router, "no ip http secure-server\n")
    insert_cfg_line(router, index_line, f"ipv6 router ospf 1\n router-id {router_id}\n")
    for interface in as_topology["routers"][router].values():
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_cfg_line(router, index_line, " ipv6 ospf 1 area 0\n")

    if is_border_routers(router, as_topology):

        index_line = find_index(router, "ip forward-protocol nd\n") - 1
        insert_cfg_line(router, index_line, "router ospf 1\n")
        index_line = find_index(router, f" router-id {router_id}\n")
        for AS_neighbor in as_topology["neighbor"]:
            if router in as_topology["neighbor"][AS_neighbor].keys():
                for interface in as_topology["neighbor"][AS_neighbor][router].values():
                    insert_cfg_line(router, index_line, f" passive-interface {interface}\n")
                    

def activate_rip(router, as_topology):
    # active RIP sur le routeur.
    rip_process_name = "process"
    index_line = find_index(router, "no ip http secure-server\n")
    insert_cfg_line(router, index_line, f"ipv6 router rip {rip_process_name}\n redistribute connected\n")
    for interface in as_topology["routers"][router].values():
        index_line = find_index(router, f"interface {interface}\n") + 4
        insert_cfg_line(router, index_line, f" ipv6 rip {rip_process_name} enable\n")


def give_router_id(router):
    x = router[1:]
    return f"{x}.{x}.{x}.{x}"


def get_subnet_interconnexion(subnet_interconnexion_dict, routeur1, routeur2):
    return subnet_interconnexion_dict[(routeur1, routeur2)] or subnet_interconnexion_dict[(routeur2, routeur1)]


def activate_bgp(router, AS, as_topology, subnet_interconnexion_dict, subnet_dict):
    """
    Active le protocole BGP sur un routeur donné en fonction de la topologie.
    """
    # Vérifier que la clé AS est valide
    if not AS.startswith("AS") or not AS[2:].isdigit():
        raise ValueError(f"Clé AS invalide détectée : {AS}")

    if "neighbor" in as_topology:
        for AS_neighbor in as_topology["neighbor"]:
            # Vérifier que la clé AS_neighbor est valide
            if not AS_neighbor.startswith("AS") or not AS_neighbor[2:].isdigit():
                raise ValueError(f"Clé AS voisine invalide détectée : {AS_neighbor}")

            for neighbor_router in as_topology["neighbor"][AS_neighbor]:
                # Choisir l'adresse IP pour BGP en fonction de l'ordre des AS
                ip = (
                    subnet_interconnexion_dict[AS][(router, neighbor_router)]
                    if int(AS[2:]) < int(AS_neighbor[2:])
                    else subnet_interconnexion_dict[AS_neighbor][(neighbor_router, router)]
                )
                # Configuration BGP (exemple)
                print(f"Configuration de BGP pour {router} avec {neighbor_router} via {ip}")


def is_border_routers(router, as_topology):
    state = False
    for AS_neighbor in as_topology["neighbor"]:
        if router in as_topology["neighbor"][AS_neighbor].keys():
            state = True
    return state

def create_networks(as_topology, router, subnet_dict, index_line):
    """
    Ajoute tous les réseaux (interfaces + loopback) dans les configurations des routeurs.
    """
    # Ajoute toutes les interfaces directement connectées au routeur
    for neighbor in as_topology["routers"][router]:
        subnet = subnet_dict.get((router, neighbor), subnet_dict.get((neighbor, router)))
        insert_cfg_line(router, index_line, f"  network {as_topology['address']}{subnet}::{as_topology['subnet_mask']}\n")
        index_line += 1
    
    # Ajoute l'interface Loopback
    insert_cfg_line(router, index_line, f"  network 2001::{router[1:]}/128\n")
    index_line += 1

def create_loopback_interface(router, as_topology):
    index_line = find_index(router, line="ip tcp synwait-time 5\n")
    insert_cfg_line(router, index_line, f"interface Loopback0\n no ip address\n ipv6 address 2001::{router[1:]}/128\n")
    index_line += 3
    if is_ospf(as_topology):
        insert_cfg_line(router, index_line, " ipv6 ospf 1 area 0\n")

if __name__ == "__main__":
    start = time.time()
    with open("no_pingable.json", 'r') as file:
        topology = json.load(file)
    main(topology)
    end = time.time()
    print(end - start)

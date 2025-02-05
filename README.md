# Network Automation Project

    Jean-Baptiste SIMON / Hugo NOEL

## Objectifs

Ce projet vise à comprendre les mécanismes du protocole de routage BGP, déployer un réseau utilisant BGP, étudier la convergence de BGP et implémenter des politiques de routage à l'aide de filtres.

## Structure du Code

Les configurations des routeurs sont générées à partir d'un fichier JSON contenant les informations nécessaires. Le projet est structuré en plusieurs modules Python, chacun ayant une responsabilité spécifique dans la configuration et la gestion des routeurs du réseau.

### Module `tools.py`

Ce module contient des fonctions utilitaires pour manipuler les fichiers de configuration des routeurs :

- `insert_line`: Insère une ligne de configuration à un index spécifique dans le fichier de configuration d'un routeur.
- `find_index`: Trouve l'index d'une ligne spécifique dans le fichier de configuration d'un routeur.
- `give_subnet_dict`: Crée un dictionnaire associant un numéro unique à chaque lien physique dans le réseau.
- `is_border_router`: Détermine si un routeur est un routeur de bordure dans son AS.
- `last_entries_subnet`: Trouve et retourne la dernière valeur de sous-réseau utilisée.
- `give_subnet_interconnexion`: Génère un dictionnaire de sous-réseaux pour les connexions inter-AS.
- `get_subnet_interconnexion`: Récupère l'adresse IPv6 d'un sous-réseau d'interconnexion entre deux routeurs.
- `generate_addresses_dict`: Génère un dictionnaire avec les voisins, interfaces, adresses IP et AS pour chaque routeur.

### Module `protocols.py`

Ce module gère l'activation des protocoles de routage sur les routeurs :

- `activate_protocols`: Active RIP ou OSPF, puis BGP pour un routeur donné.
- `give_ID`: Génère un ID unique pour un routeur.
- `is_rip`: Vérifie si RIP doit être activé pour un AS donné.
- `activate_rip`: Active RIP sur un routeur donné pour toutes ses interfaces.
- `is_ospf`: Vérifie si OSPF doit être activé pour un AS donné.
- `activate_ospf`: Active OSPF sur un routeur donné pour toutes ses interfaces.
- `activate_bgp`: Active BGP sur un routeur donné en utilisant les adresses Loopback de ses voisins.

### Module `addresses.py`

Ce module gère la création des fichiers de configuration de base et des interfaces pour les routeurs :

- `create_base_cfg`: Crée le fichier de configuration de base pour un routeur.
- `create_loopback_interface`: Insère les lignes de configuration pour l'interface Loopback d'un routeur.
- `create_interfaces`: Génère les interfaces avec les adresses IPv6 correctes pour chaque routeur de chaque AS.

### Module `main.py`

Ce module est le point d'entrée principal du projet. Il lit le fichier JSON de topologie et génère les configurations des routeurs en utilisant les modules précédents.

### Module `move_files.ipynb`

Ce module gère le déplacement des fichiers de configuration générés vers les répertoires appropriés dans GNS3 :

- `get_number_file`: Extrait le numéro du nom de fichier s'il est dans le format correct.
- `compare_and_paste`: Compare les fichiers dans les répertoires source et destination et les déplace si nécessaire.

## Lancer les Scripts

Pour exécuter le script principal et générer les configurations des routeurs, utilisez la commande suivante :

```bash
python main.py
```

Le fichier `intends.json` doit contenir les informations nécessaires pour configurer les routeurs des différents AS. Le script `main.py` lit ce fichier JSON et génère les configurations des routeurs en conséquence.

Pour déplacer les fichiers de configuration générés vers les répertoires appropriés dans GNS3, exécutez le notebook `move_files.ipynb`.

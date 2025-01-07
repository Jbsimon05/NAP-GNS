# Network Automation Project

## Plan d'adressage

### AS X (RIP)
- **Loopback interfaces**: 2001:db8:1::/64
- **Physical interfaces**: 2001:db8:2::/64

### AS Y (OSPF)
- **Loopback interfaces**: 2001:db8:3::/64
- **Physical interfaces**: 2001:db8:4::/64

## Configuration des routeurs

Les configurations des routeurs sont générées à partir d'un fichier JSON contenant les informations nécessaires. Le script Python `generate_config.py` lit ce fichier JSON et génère les configurations des routeurs.

### Fichier JSON de configuration

Le fichier `config.json` contient les informations nécessaires pour configurer les routeurs des deux AS.

### Script Python

Le script `generate_config.py` lit le fichier JSON et génère les configurations des routeurs. Pour exécuter le script, utilisez la commande suivante :

```bash
python generate_config.py

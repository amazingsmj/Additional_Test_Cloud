# Automatisation de la Création de Machines Virtuelles sur VMware ESXi avec PyVmomi

## Description
Il s'agit d'un ensemble de scripts visant à automatiser et simplifier le processus de création de machines virtuelles à l'aide de PyVmomi, une bibliothèque Python permettant d'interagir avec l'API vSphere de VMware. Grâce à PyVmomi, les développeurs peuvent écrire des scripts python pour créer, modifier et gérer des machines virtuelles sur un environnement ESXi, ce qui permet aux administrateurs système d'économiser du temps et des efforts en automatisant ces tâches.

## Objectifs Principaux :
1. Déploiement d'Images OVA :
   Le projet commence par le déploiement d'une image OVA (tinyVM) à travers le fichier 7_deployer_OVA.py. Un fichier de configuration au format JSON : config.json, spécifie le nombre d'instances à déployer sur l'ESXi.
2. Clonage d'OVA :
   Pour déployer plusieurs instances de la même OVA, le projet inclut des fonctionnalités de clonage grace au fichier 8_cloner_vm.py. Le fichier de configuration config.json indiquera le nombre de machines virtuelles à créer.
3. Création de Machines Virtuelles à partir de Zéro :
   Le projet permet également la création de machines virtuelles "from scratch", ceci par l'exéution successive des fichiers 9_1_vm_fom_scratch.py, 9_2_vm_fom_scratch.py, et 9_3_vm_fom_scratch.py. Le fichier de configuration JSON config.json définit les paramètres minimaux, tels que la RAM, la taille du disque et le CD-ROM.


## Table des Matières
* Prérequis
* Structure du Projet
* Utilisation
* Difficultés Rencontrées et Solutions
* Scripts complémentaires


## Prérequis
Avant de démarrer, assurez-vous d’avoir 
1. Un environnement Python avec les packages suivants installés :
   * pyvmomi
   * json
   * ssl
  
2. Un accès à un serveur vSphere avec les autorisations nécessaires pour créer, configurer et gérer des VM.
3. Un fichier OVA valide à déployer et un fichier ISO pour la configuration des lecteurs CD-ROM.
4. Un fichier de configuration JSON (conf.json) avec les paramètres suivants :
   ``` {
    "center_host": "votre_vSphere_center_host",
    "admin_user": "votre_vSphere_nom_utilisateur",
    "password": "votre_vSpher_password",
    "template_vm_name": "votre_template_vm_name",
    "vm_name": "vm_name",
    "datacenter_name": "datacenter_name",
    "vm_folder": "vm_folder", 
    "new_vm_name": "new_vm_name",
    "data_store": "data_store", 
    "cluster_name": "cluster_name",
    "resource_pool": "resource_pool",
    "power_on": true,
    "ova_files": "ova_files",
    "iso_path": "iso_path",
    "core_vm_name": "core_vm_name",
    "new_core_vm_name": "new_core_vm_name",
    "number_of_instances": number_of_instances,
    "number_of_clones": number_of_clones,
    "memory_mb": memory_mb,
    "disk_size": disk_size,
    "number_of_cpu": number_of_cpu,
    "disable_ssl_verification": true
}```

## Structure du Projet
Le projet est divisé en plusieurs fonctions dans des scripts Python :
1. Connexion à vSphere - connect_to_vsphere() : Établit une connexion avec le serveur vSphere.
2. Déploiement d'une VM depuis un OVA - deploy_ova() : Déploie une VM à partir d’un fichier OVA.
3. Déploiement d'un modèle de VM pour clonage - deploy_template_vm() : Déploie une VM en tant que modèle, facilitant la création de clones.
4. Clonage de VM depuis le modèle - clone_vm() : Clone le modèle de VM pour déployer plusieurs instances.
5. Création d'une VM vide - create_dummy_vm() : Crée une VM vide avec des spécifications de base.
6. Configuration du lecteur CD-ROM - configure_cdrom() : Configure le lecteur CD-ROM pour utiliser un fichier ISO.
7. Démarrage de la VM - start_vm() : Allume la VM spécifiée.

## Utilisation
1. Configurer le fichier conf.json : Assurez-vous que les valeurs de conf.json correspondent aux informations de votre environnement vSphere.
2. Exécuter le script principal : Lancez main() pour démarrer l'ensemble du processus de déploiement et de configuration.
3. Les scripts peuvent être adaptés en fonction des besoins de votre environnement, en changeant le nombre de VM déployées, la mémoire et le disque alloués, etc.


## Difficultés Rencontrées et Solutions
1. Erreurs SSL lors de la Connexion à vSphere
   * Problème : Des erreurs SSL, telles que ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:2406), peuvent survenir lors de la connexion au serveur vSphere.
   * Solution : Le script utilise disableSslCertValidation=True ou un contexte SSL non sécurisé (créé avec ssl._create_unverified_context()). Cela désactive la vérification SSL pour contourner le problème. Attention : Cette solution est utile pour les environnements de test. Pour un environnement de production, il est recommandé de configurer des certificats SSL valides.

2. Problèmes de Chemins d'Accès des Fichiers OVA et ISO
   * Problème : Les chemins d'accès aux fichiers OVA et ISO peuvent entraîner des erreurs si les chemins sont incorrects ou inaccessibles.
   * Solution : Assurez-vous que les chemins dans conf.json sont corrects et accessibles. Le format du chemin ISO doit correspondre au stockage de données sur ESXi (ex. : DB1/test/Core-5.4.iso).

3.Déploiement du Modèle et Clonage
   * Problème : Lors du clonage, nous avons systématiquement l'erreur "The operation is not supported on the object.", qui se déclenche soit lorsque le fichier OVA n'est pas préparé pour le clonage, ou soit par un rejet par l'interface de l'ESXi pour des raisons de compatibilités avec l'objet cible dans l'environnement vSphere. On peut aussi noter les raisons suivantes :
     - Restrictions de l'hôte ou de la version d'ESXi
     - Permissions Insuffisantes
     - Mauvais objet cible dans le code
     - Propriétés Non Valides dans config.json
   * Solution : Mettre sur pieds une logigue de clonage en exploitant le code du fichier 7_deployer_OVA.py pour déployer une ou plusieurs instances de la vm + une autre logique permettant de renommer la vm déployée (juste après son déploiement).

4.Gestion des Tâches et Délai d'Attente
   * Problème : Certaines opérations peuvent être longues, et attendre en boucle peut bloquer le script
   * Solution : Le script inclut time.sleep(1) dans les boucles d’attente pour éviter une surcharge. En cas de déploiement de nombreuses instances, une gestion plus avancée des tâches, comme l’utilisation de threads, pourrait être envisagée.

5. Privilèges et Permissions Insuffisants
   * Problème : Des erreurs peuvent apparaître si l’utilisateur n’a pas les droits nécessaires pour créer et configurer des VM.
   * Solution : Assurez-vous que le compte vSphere utilisé a les permissions requises pour les opérations de déploiement, de clonage et de reconfiguration de VM.


## Scripts complémentaires :
Il s'agit principalement de codes pythons ayant servi à comprendre le sujet et à mettre sur pieds des astuces pour certaines logiques, ainsi que de certains codes de la bibliothèque PyVmomi permettant de pour atteindre les objectifs. Ces codes sont : 
* list_folders_&_vms.py : conçu pour interagir avec un serveur vSphere ou ESXi en utilisant la bibliothèque PyVmomi, il permet surtout de lister les repertoires du datastore ainsi que leur contnu, et d'afficher les machines virtuelles (VMs) présentes sur la vSphere.
* list_folders.py : c'est juste un prototype moins élaboré de list_folders_&_vms.py car il se limite à lister les repertoires du datastore.
* rename_vm.py : il permet surtout de lister les machines virtuelles (VMs) déployées sur l'hôte ESXi et les affiche, puis permet à l'utilisateur de renommer une machine virtuelle spécifiée. Pour choisir la vm à renommer, il est demandé à l'uitilisateur d'entrer le nom de la vm parmis celles affichées, puis il lui est demandé d'entrer le nouveau nom de la vm.
* rename_vm_2.py : pareil à rename_vm.py, à la seule différence que la vm à renommer est récupérée à partir de son indice dans la liste des VMs déployées sur l'hôte de l'ESXi.
* service_instance.py : script fournit par la documentation de la bibliothèque PyVmomi, il nous a permet de comprendre la logique du processus de connexion à un hôte VMware vSphere ou ESXi tout en gérant les aspects de sécurité liés à SSL.
* tasks.py : autre code issue de la documentation de la bibliothèque PyVmomi, et écrit par Michael Rice, définit un module d'assistance pour gérer les opérations de tâches dans un environnem.
* pchelper.py : autre code provenant de la documentation de la bibliothèque PyVmomi, définit un module d'assistance pour collecter des propriétés d'objets gérés dans un environnement VMware en utilisant la bibliothèque PyVmomi.
* cli.py : autre code provenant de la documentation de la bibliothèque PyVmomi, définit un module qui facilite la gestion des arguments de ligne de commande pour interagir avec l'API vSphere de VMware. Il utilise la bibliothèque argparse pour traiter les arguments et inclut des fonctions auxiliaires pour simplifier la configuration des arguments requis pour les échantillons de code.
* add_nic_to_vm.py : autre code provenant de la documentation de la bibliothèque PyVmomi,conçu pour ajouter une carte réseau (NIC) à une machine virtuelle dans un environnement VMware vSphere en utilisant l'API vSphere via la bibliothèque pyVmomi.




   



# Déploiement Automatisé de VM sur vSphere

Ce projet propose une série de scripts en Python pour automatiser le déploiement de machines virtuelles (VM) sur une infrastructure vSphere. Le script permet la connexion au serveur vSphere, le déploiement d'une VM à partir d'un fichier OVA, le clonage de VM à partir d'un modèle, ainsi que la configuration et le démarrage de nouvelles instances.

## Table des Matières
* Prérequis
* Structure du Projet
* Utilisation
* Difficultés Rencontrées et Solutions
* Crédits


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
    "vsphere_host": "votre_adresse_vsphere",
    "vsphere_user": "votre_utilisateur",
    "vsphere_password": "votre_mot_de_passe",
    "ova_path": "/chemin/vers/fichier.ova",
    "iso_path": "DB1/test/Core-5.4.iso",
    "number_of_instances": 2,
    "template_vm_name": "Nom_du_modèle_VM",
    "ram": 2048,
    "disk_size": 10
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
   * Problème : Lors du clonage, le modèle de VM doit être éteint, sinon le script retourne une erreur.
   * Solution : Avant de cloner la VM, le script vérifie que le modèle est arrêté. Les datastores et pools de ressources utilisés sont les premiers identifiés dans la hiérarchie vSphere. Ajustez ces choix si nécessaire pour sélectionner des ressources spécifiques.

4.Gestion des Tâches et Délai d'Attente
   * Problème : Certaines opérations peuvent être longues, et attendre en boucle peut bloquer le script
   * Solution : Le script inclut time.sleep(1) dans les boucles d’attente pour éviter une surcharge. En cas de déploiement de nombreuses instances, une gestion plus avancée des tâches, comme l’utilisation de threads, pourrait être envisagée.

5. Privilèges et Permissions Insuffisants
   * Problème : Des erreurs peuvent apparaître si l’utilisateur n’a pas les droits nécessaires pour créer et configurer des VM.
   * Solution : Assurez-vous que le compte vSphere utilisé a les permissions requises pour les opérations de déploiement, de clonage et de reconfiguration de VM.



   



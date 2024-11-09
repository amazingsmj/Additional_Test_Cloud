import json
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def load_config(file_path):
    """Charge les paramètres de connexion et de VM depuis un fichier JSON."""
    with open(file_path, 'r') as f:
        return json.load(f)

def list_vms(content):
    """Récupère la liste de toutes les VMs déployées sur l'hôte ESXi."""
    vms = []
    for datacenter in content.rootFolder.childEntity:
        vm_folder = datacenter.vmFolder
        vm_list = vm_folder.childEntity
        for vm in vm_list:
            if isinstance(vm, vim.VirtualMachine):
                vms.append(vm)
    return vms

def rename_vm(vm, new_name):
    """Renomme la VM spécifiée."""
    try:
        old_name = vm.name
        vm.Rename(new_name)
        print(f"La VM '{old_name}' a été renommée en '{new_name}' avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors du renommage de la VM : {e}")
        return False
    

def main():
    # Charger la configuration depuis le fichier config.json
    config_file_path = "config.json"
    config = load_config(config_file_path)
    
    # Désactiver la vérification SSL si spécifié dans la configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if config.get("disable_ssl_verification", False):
        context.check_hostname = False  # Désactiver check_hostname pour éviter le conflit
        context.verify_mode = ssl.CERT_NONE

    # Connexion à l'hôte ESXi
    try:
        service_instance = SmartConnect(
            host=config["center_host"],
            user=config["admin_user"],
            pwd=config["password"],
            sslContext=context
        )
        print("Connexion établie avec succès à l'hôte ESXi.")
    except Exception as e:
        print(f"Erreur de connexion à l'hôte ESXi : {e}")
        return

    # Obtenir l'objet de contenu de la racine
    content = service_instance.RetrieveContent()

    # Récupérer et afficher la liste des VMs déployées
    vms = list_vms(content)
    if not vms:
        print("Aucune VM déployée trouvée.")
        Disconnect(service_instance)
        return

    print("Liste des VMs déployées :")
    for index, vm in enumerate(vms, start=1):
        print(f"{index}. {vm.name}")

    # Demander à l'utilisateur de sélectionner une VM à renommer par son numéro
    try:
        vm_index = int(input("Entrez le numéro de la VM que vous souhaitez renommer : ")) - 1
        selected_vm = vms[vm_index]
    except (ValueError, IndexError):
        print("Numéro de VM invalide. Veuillez réessayer avec un numéro correct.")
        Disconnect(service_instance)
        return

    # Demander le nouveau nom de la VM
    new_vm_name = input("Veuillez entrer le nouveau nom de la VM : ")
    # Renommer la VM
    rename_vm(selected_vm, new_vm_name)

    # Déconnexion de l'hôte ESXi
    Disconnect(service_instance)
    print("Déconnexion de l'hôte ESXi.")

if __name__ == "__main__":
    main()

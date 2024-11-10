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
    config_file_path = "config.json"
    config = load_config(config_file_path)
    
    # Disable SSL checking if specified in configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if config.get("disable_ssl_verification", False):
        context.check_hostname = False  # Disable check_hostname to avoid conflict
        context.verify_mode = ssl.CERT_NONE

    # Connecting to ESXi Host
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

    # Get content object from root
    content = service_instance.RetrieveContent()

    # Retrieve and display the list of deployed VMs
    vms = list_vms(content)
    if not vms:
        print("Aucune VM déployée trouvée.")
        Disconnect(service_instance)
        return

    print("Liste des VMs déployées :")
    for index, vm in enumerate(vms, start=1):
        print(f"{index}. {vm.name}")

    # Ask the user to select a VM to rename by its number
    try:
        vm_index = int(input("Entrez le numéro de la VM que vous souhaitez renommer : ")) - 1
        selected_vm = vms[vm_index]
    except (ValueError, IndexError):
        print("Numéro de VM invalide. Veuillez réessayer avec un numéro correct.")
        Disconnect(service_instance)
        return

    
    new_vm_name = input("Veuillez entrer le nouveau nom de la VM : ")
    
    rename_vm(selected_vm, new_vm_name)

    Disconnect(service_instance)
    print("Déconnexion de l'hôte ESXi.")

if __name__ == "__main__":
    main()

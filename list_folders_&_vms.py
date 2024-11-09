import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def connect_to_vsphere(host, user, password):
    """Connect to vSphere or ESXi server."""
    context = ssl._create_unverified_context()
    try:
        service_instance = SmartConnect(host=host, user=user, pwd=password, sslContext=context)
        atexit.register(Disconnect, service_instance)
        print("Connected to vSphere")
        return service_instance
    except Exception as e:
        print(f"Failed to connect to vSphere: {e}")
        return None

def get_datastore(content, datastore_name):
    """Retrieve the datastore object by name."""
    for datacenter in content.rootFolder.childEntity:
        for datastore in datacenter.datastore:
            if datastore.name == datastore_name:
                print(f"Datastore '{datastore_name}' found.")
                return datastore
    print(f"Datastore '{datastore_name}' not found.")
    return None

def list_datastore_files(datastore, folder_path=""):
    """List all files and folders in a datastore path."""
    browser = datastore.browser
    search_spec = vim.host.DatastoreBrowser.SearchSpec()

    # Perform the search on the datastore path
    datastore_path = f"[{datastore.name}] {folder_path}"
    task = browser.SearchDatastoreSubFolders_Task(datastore_path, search_spec)
    while task.info.state not in ["success", "error"]:
        pass

    if task.info.state == "error":
        print("Error retrieving files:", task.info.error)
        return

    # List all files and folders
    for result in task.info.result:
        print(f"\nDirectory: {result.folderPath}")
        for file in result.file:
            print(f" - {file.path}")

def get_vm_folder_path(vm, datacenter):
    """Récupérer le chemin complet du dossier où se trouve la VM."""
    parent = vm.parent
    path = []
    
    # Afficher le parent de la VM
    print(f"Parent de la VM {vm.name}: {parent}")
    
    # Si la VM est directement dans le dossier racine du datacenter
    if parent == datacenter.vmFolder:
        return ""

    while parent != datacenter.vmFolder:
        if isinstance(parent, vim.Folder):
            path.append(parent.name)
        parent = parent.parent

    # Reverse the path to get the correct order from root to the VM
    path.reverse()
    return "/".join(path)


def list_vms(content):
    """List all VMs in the datacenter."""
    for datacenter in content.rootFolder.childEntity:
        print(f"\nListing VMs in Datacenter: {datacenter.name}")
        for vm in datacenter.vmFolder.childEntity:
            if isinstance(vm, vim.VirtualMachine):
                # Get the folder path for the VM
                folder_path = get_vm_folder_path(vm, datacenter)
                print(f" - VM: {vm.name} (Path: {folder_path})")

def main():
    # Configuration
    host = "10.144.208.236"           # IP de votre hôte ESXi ou vCenter
    user = "root"               # Nom d'utilisateur pour ESXi/vCenter
    password = "toto32.."       # Mot de passe
    datastore_name = "datastore1"  # Nom du datastore
    folder_path = ""            # Chemin du dossier à lister (laisser vide pour la racine)

    # Connexion à vSphere
    si = connect_to_vsphere(host, user, password)
    if not si:
        return

    # Récupération du contenu
    content = si.RetrieveContent()

    # Récupération du datastore
    datastore = get_datastore(content, datastore_name)
    if not datastore:
        return

    # Lister les dossiers et fichiers dans le datastore
    list_datastore_files(datastore, folder_path)

    # Lister les VMs dans le datacenter
    list_vms(content)

if __name__ == "__main__":
    main()

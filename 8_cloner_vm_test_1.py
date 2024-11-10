import json
from pyVmomi import vim
from clone_vm import clone_vm
import service_instance, pchelper

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def list_vms(content):
    vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in vm_list.view:
        print("VM Name: ", vm.name, " - Template: ", vm.config.template)
        
    vm_list.Destroy()

def main():
    # Charger la configuration
    config = load_config('config.json')

    # Connexion à l'instance de service 
    si = service_instance.connect(config['center_host'], config['admin_user'], config['password'])

    content = si.RetrieveContent()
    list_vms(content) 
    
    # Récupération du template de la VM
    template = pchelper.get_obj(content, [vim.VirtualMachine], config['template_vm_name'])

    if template:
        if not template.config.template:
            print(f"{config['template_vm_name']} n'est pas un modèle de VM.")
            return

        # Cloner la VM
        clone_vm(
            content,
            template,
            config['new_vm_name'],  
            config['datacenter_name'],
            config['vm_folder'],
            config['data_store'],
            config['cluster_name'],
            config['resource_pool'],
            config['power_on']
        )
    else:
        print("Template VM non trouvé.")

if __name__ == "__main__":
    main()

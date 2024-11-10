import json
from pyVmomi import vim
from clone_vm import clone_vm
import service_instance, pchelper

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def list_vms(content):
    vm_list = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    print("Les VMs déployées sont : ")
    for vm in vm_list.view:
        #print("\tVM Name: ", vm.name)
        print("\t", vm.name)
    vm_list.Destroy()

def main():
    # Loading configurations
    config = load_config('config.json')

    # Connection to the service instance 
    si = service_instance.connect(config['center_host'], config['admin_user'], config['password'])

    content = si.RetrieveContent()
    
    # List the available VMs
    list_vms(content)

    # Get the VM template
    template = pchelper.get_obj(content, [vim.VirtualMachine], config['template_vm_name'])

    if template:
        # Clone the VM
        clone_vm(
            content,
            template,
            config['new_vm_name'],
            config['datacenter_name'],
            config['vm_folder'],
            config['data_store'],
            config['cluster_name'],
            config['resource_pool'],
            config['power_on'],
            None  # no datastore cluster specified
        )
    else:
        print("Template VM non trouvé.")

if __name__ == "__main__":
    main()

import json
import time
from pyVmomi import vim
import cli, service_instance, tasks, pchelper
from add_nic_to_vm import add_nic
from pyVim.connect import SmartConnect, Disconnect

# Charger la configuration depuis le fichier config.json vm_name
def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def create_empty_vm(new_core_vm_name, si, vm_folder, resource_pool, datastore, memory_mb, num_cpus, disk_size):
    """Crée une VM vide avec la configuration spécifiée."""
    datastore_path = f'[{datastore}] {new_core_vm_name}'
    
    # Configure the basic VMX file, without disk
    vmx_file = vim.vm.FileInfo(
        logDirectory=None,
        snapshotDirectory=None,
        suspendDirectory=None,
        vmPathName=datastore_path
    )
    
    config_spec = vim.vm.ConfigSpec(
        name=new_core_vm_name,
        memoryMB=memory_mb,
        numCPUs=num_cpus,
        files=vmx_file,
        guestId='otherGuest',  
        version='vmx-07'
    )
    
    print(f"Création de la VM {new_core_vm_name}...")
    task = vm_folder.CreateVM_Task(config=config_spec, pool=resource_pool)
    tasks.wait_for_tasks(si, [task])

def main():
    config = load_config('config.json')  

    si = SmartConnect(
    host=config['center_host'],
    user=config['admin_user'],
    pwd=config['password'],
    disableSslCertValidation=True 
)

    content = si.RetrieveContent()
    vm_folder = pchelper.get_obj(content, [vim.Folder], config['vm_folder'])
    resource_pool = pchelper.get_obj(content, [vim.ResourcePool], config['resource_pool'])
    datastore = config['data_store']
    
    # Creation of several VM instances
    for i in range(config['number_of_instances']):
        vm_name = f"{config['new_core_vm_name']}_{i + 1}"
        create_empty_vm(
            vm_name,
            si,
            vm_folder,
            resource_pool,
            datastore,
            config['memory_mb'],
            config['number_of_cpu'],
            config['disk_size']
        )

    print(f"{config['number_of_instances']} VM(s) créées avec succès.")

if __name__ == "__main__":
    main()

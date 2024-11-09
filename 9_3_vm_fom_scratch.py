from pyVmomi import vim
from pyVim.task import WaitForTask
import json
from pyVim.connect import SmartConnect, Disconnect

# Charger la configuration depuis le fichier config.json vm_name
def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def get_vm(si, core_vm_name, datacenter_name):
    """Récupérer la VM spécifiée."""
    content = si.RetrieveContent()
    datacenter = next((dc for dc in content.rootFolder.childEntity if dc.name == datacenter_name), None)
    if not datacenter:
        raise Exception(f"Datacenter '{datacenter_name}' non trouvé.")
    return next((vm for vm in datacenter.vmFolder.childEntity if vm.name == core_vm_name), None)

def add_cdrom(si, core_vm_name, iso_path, datacenter_name):
    """Ajouter un lecteur CD-ROM à la VM et attacher l'image ISO."""
    vm = get_vm(si, core_vm_name, datacenter_name)
    if not vm:
        raise Exception(f"VM '{core_vm_name}' non trouvée dans le datacenter '{datacenter_name}'.")

    controller = next((dev for dev in vm.config.hardware.device if isinstance(dev, vim.vm.device.VirtualIDEController) and len(dev.device) < 2), None)
    if not controller:
        raise Exception("Contrôleur IDE libre non trouvé.")

    device_spec = vim.vm.device.VirtualDeviceSpec()
    device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    cdrom_backing = vim.vm.device.VirtualCdrom.IsoBackingInfo(fileName=iso_path)
    
    cdrom = vim.vm.device.VirtualCdrom()
    cdrom.backing = cdrom_backing
    cdrom.connectable = vim.vm.device.VirtualDevice.ConnectInfo(allowGuestControl=True, startConnected=True)
    cdrom.controllerKey = controller.key
    cdrom.key = -1
    device_spec.device = cdrom

    config_spec = vim.vm.ConfigSpec(deviceChange=[device_spec])
    WaitForTask(vm.Reconfigure(config_spec))
    print(f"CD-ROM ajouté et ISO attachée à la VM '{core_vm_name}'.")

def start_vm(si, core_vm_name, datacenter_name):
    """Démarrer la VM spécifiée."""
    vm = get_vm(si, core_vm_name, datacenter_name)
    if not vm:
        raise Exception(f"VM '{core_vm_name}' non trouvée dans le datacenter '{datacenter_name}'.")
    
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
        try:
            WaitForTask(vm.PowerOnVM_Task())
            print(f"VM '{core_vm_name}' démarrée avec succès.")
        except vim.fault.GenericVmConfigFault as e:
            print(f"Erreur de configuration de la VM lors du démarrage de '{core_vm_name}': {e.msg}")
            print("Conseil : Vérifiez que l'hôte supporte Intel VT-x ou AMD-V et que la virtualisation est activée.")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors du démarrage de la VM '{core_vm_name}': {e}")
    else:
        print(f"La VM '{core_vm_name}' est déjà en cours d'exécution.")

def main():
    config = load_config('config.json')
    si = SmartConnect(
        host=config['center_host'],
        user=config['admin_user'],
        pwd=config['password'],
        disableSslCertValidation=config['disable_ssl_verification']
    )

    try:
        add_cdrom(si, config['core_vm_name'], config['iso_path'], config['datacenter_name'])
        start_vm(si, config['core_vm_name'], config['datacenter_name'])
    finally:
        Disconnect(si)

if __name__ == "__main__":
    main()

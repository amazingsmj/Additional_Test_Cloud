import json
import ssl
import tarfile
import os
import time
from threading import Timer
from six.moves.urllib.request import Request, urlopen
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import atexit

class OvfHandler:
    def __init__(self, ova_path):
        self.handle = self._create_file_handle(ova_path)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovf_file = next(f for f in self.tarfile.getnames() if f.endswith(".ovf"))
        self.descriptor = self.tarfile.extractfile(ovf_file).read().decode()
        self.file_items = [f for f in self.tarfile.getnames() if f.endswith(('.vmdk', '.vmdk-sparse'))]

    def _create_file_handle(self, entry):
        if os.path.exists(entry):
            return FileHandle(entry)
        return WebHandle(entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        self.spec = spec

    def get_disk(self, file_item):
        ovf_filename = next(f for f in self.tarfile.getnames() if f == file_item.path)
        return self.tarfile.extractfile(ovf_filename)

    def get_device_url(self, file_item, lease):
        for device_url in lease.info.deviceUrl:
            if device_url.importKey == file_item.deviceId:
                return device_url
        raise Exception("Failed to find deviceUrl for file %s" % file_item.path)

    def upload_disks(self, lease, host):
        self.lease = lease
        try:
            self.start_timer()
            for file_item in self.spec.fileItem:
                self.upload_disk(file_item, lease, host)
            lease.Complete()
            print("Finished deploy successfully.")
            return 0
        except vmodl.MethodFault as ex:
            print("Hit an error in upload: %s" % ex)
            lease.Abort(ex)
        except Exception as ex:
            print("Lease: %s" % lease.info)
            print("Hit an error in upload: %s" % ex)
            lease.Abort(vmodl.fault.SystemError(reason=str(ex)))
        return 1

    def upload_disk(self, file_item, lease, host):
        ovf_file = self.get_disk(file_item)
        if ovf_file is None:
            return
        device_url = self.get_device_url(file_item, lease)
        url = device_url.url.replace('*', host)
        headers = {'Content-length': str(get_tarfile_size(ovf_file))}
        if hasattr(ssl, '_create_unverified_context'):
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None
        req = Request(url, ovf_file.read(), headers=headers)
        urlopen(req, context=ssl_context)

    def start_timer(self):
        Timer(5, self.timer).start()

    def timer(self):
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done, vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progress: %d%%\r" % prog)
        except Exception:
            pass

def connect_to_vsphere(host, user, password):
    try:
        service_instance = SmartConnect(host=host, user=user, pwd=password, disableSslCertValidation=True)
        atexit.register(Disconnect, service_instance)
        print("Connecté à vSphere")
        return service_instance
    except Exception as e:
        print(f"Erreur de connexion à vSphere : {e}")
        return None

def deploy_ova(si, config):
    try:
        data_center = si.content.rootFolder.childEntity[0]
        vm_folder = data_center.vmFolder
        resource_pool = data_center.hostFolder.childEntity[0].resourcePool
        datastore = next(ds for ds in data_center.datastore if ds.name == config["data_store"])

        # Gestion de l'OVA
        ovf_manager = si.content.ovfManager
        ovf_handle = OvfHandler(config["ova_files"])

        import_spec_params = vim.OvfManager.CreateImportSpecParams()
        import_spec = ovf_manager.CreateImportSpec(
            ovf_handle.get_descriptor(), resource_pool, datastore, import_spec_params
        )
        ovf_handle.set_spec(import_spec)

        # Vérification des erreurs d'importation
        if import_spec.error:
            for error in import_spec.error:
                print(f"Erreur d'importation de l'OVA : {error}")
            return

        lease = resource_pool.ImportVApp(import_spec.importSpec, vm_folder)
        while lease.state == vim.HttpNfcLease.State.initializing:
            time.sleep(1)

        if lease.state == vim.HttpNfcLease.State.error:
            print(f"Erreur de lease : {lease.error}")
            return

        # Chargement des disques
        ovf_handle.upload_disks(lease, config["center_host"])

    except Exception as e:
        print(f"Erreur lors du déploiement de l'OVA : {e}")


def get_tarfile_size(tarfile):
    if hasattr(tarfile, 'size'):
        return tarfile.size
    size = tarfile.seek(0, 2)
    tarfile.seek(0, 0)
    return size

class FileHandle(object):
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'rb')
        self.st_size = os.stat(filename).st_size
        self.offset = 0

    def __del__(self):
        self.fh.close()

    def tell(self):
        return self.fh.tell()

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset
        return self.fh.seek(offset, whence)

    def seekable(self):
        return True

    def read(self, amount):
        self.offset += amount
        result = self.fh.read(amount)
        return result

    def progress(self):
        return int(100.0 * self.offset / self.st_size)

class WebHandle(object):
    def __init__(self, url):
        self.url = url
        r = urlopen(url)
        if r.code != 200:
            raise FileNotFoundError(url)
        self.headers = self._headers_to_dict(r)
        if 'accept-ranges' not in self.headers:
            raise Exception("Site does not accept ranges")
        self.st_size = int(self.headers['content-length'])
        self.offset = 0

    def _headers_to_dict(self, r):
        result = {}
        if hasattr(r, 'getheaders'):
            for n, v in r.getheaders():
                result[n.lower()] = v.strip()
        else:
            for line in r.info().headers:
                if line.find(':') != -1:
                    n, v = line.split(': ', 1)
                    result[n.lower()] = v.strip()
        return result

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset
        return self.offset

    def seekable(self):
        return True

    def read(self, amount):
        start = self.offset
        end = self.offset + amount - 1
        req = Request(self.url, headers={'Range': 'bytes=%d-%d' % (start, end)})
        r = urlopen(req)
        self.offset += amount
        result = r.read(amount)
        r.close()
        return result

    def progress(self):
        return int(100.0 * self.offset / self.st_size)

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    si = connect_to_vsphere(config["center_host"], config["admin_user"], config["password"])

    if si:
        for i in range(config["number_of_instances"]):
            for j in range(config["number_of_clones"]):
                vm_name = f"{config['vm_name']}"
                print(f"Deploying VM: {vm_name}")
                try:
                    deploy_ova(si, config)
                    print(f"vm : {vm_name} deployed successfull !")
                except Exception as e:
                    print(f"Error deploying VM {vm_name}: {e}")

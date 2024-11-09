"""
This module implements simple helper functions for managing service instance objects
"""
__author__ = "VMware, Inc."

import atexit
from pyVim.connect import SmartConnect, Disconnect


def connect(host, user, password, port=443, disable_ssl_verification=True):
    service_instance = None

    try:
        if disable_ssl_verification:
            service_instance = SmartConnect(host=host,
                                            user=user,
                                            pwd=password,
                                            port=port,
                                            disableSslCertValidation=True)
        else:
            service_instance = SmartConnect(host=host,
                                            user=user,
                                            pwd=password,
                                            port=port)
        
        atexit.register(Disconnect, service_instance)
    except IOError as io_error:
        print(io_error)

    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied credentials.")

    return service_instance

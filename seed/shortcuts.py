from seed.profiles.utils import Struct
from seed.utils import obtain_instances
from seed.utils.api import obtain_driver, obtain_instances

def obtain_driver_by_name(libcloud_driver_name):
    return obtain_driver(Struct({'driver': libcloud_driver_name}))

def obtain_instance_by_driver_uuid(libcloud_dirver, instance_uuid):
    try:
        return obtain_instances(libcloud_driver, [instance_uuid])[0]
    except IndexError:
        return None
    

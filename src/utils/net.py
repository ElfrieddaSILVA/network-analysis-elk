import traceback

from contextlib import contextmanager

from mininet.net import Containernet
from mininet.log import info

from .logger import Logger


@contextmanager
def containernet_handler(*args, **kwargs):
    
    net = Containernet(*args, **kwargs)

    try:
        yield net
    except Exception as e:
        tb = traceback.format_exc()
        Logger.warn(tb)
        Logger.warn(e)
    finally:    
        info('*** Stopping network')
        net.stop()

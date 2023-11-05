import trakt
from os import environ, path, makedirs
import platform
import trakt.core
from trakt.core import CORE

def check_config():
    if "XDG_DATA_HOME" in environ:
        data_dir = environ["XDG_DATA_HOME"]
    elif platform.system() == "Windows":
        data_dir = path.expanduser("~/.traktexport")
    else:
        data_dir = path.expanduser("~/.local/share")
    makedirs(data_dir, exist_ok=True)

    default_cfg_path = path.join(data_dir, "traktexport.json")
    traktexport_cfg = environ.get("TRAKTEXPORT_CFG", default_cfg_path)
    trakt.core.CONFIG_PATH = traktexport_cfg

    if not path.exists(default_cfg_path):
        return False
    
    return True

def authenticate(username : str, client_id : str, client_secret : str):
       
    trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH

    if check_config():
        CORE._bootstrap()
    else:
        trakt.init(username, client_id=client_id, client_secret=client_secret, store=True)
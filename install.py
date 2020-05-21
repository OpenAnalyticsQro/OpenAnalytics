# this script is used to initialize all env variables
import dotenv
import os
from CommonOA import APP_NAME_ENV, CREDENTIALS_PATH_ENV, PICKLE_PATH_ENV
from Logger import mainLogger as Log

CRED_FOLDER = "Credentials"
PICKLE_FOLDER = "PickleOA"


def install_internals_paths():
    """ install internal paths """
    path_file = os.path.abspath(__file__)
    path_dir = os.path.dirname(path_file)
    path_cred = os.path.join(path_dir, CRED_FOLDER)
    path_pickle = os.path.join(path_dir, PICKLE_FOLDER)

    if os.path.isdir(path_cred):
        # valid path
        Log.info(f"Generating CREDENTIALS_PATH: {path_cred}")
        dotenv.set_key(dotenv.find_dotenv(), CREDENTIALS_PATH_ENV, path_cred)
    else:
        Log.error(f"Inalid CREDENTIALS_PATH: {path_cred}")

    if os.path.isdir(path_pickle):
        # valid path
        Log.info(f"Generating PICKLE_PATH: {path_pickle}")
        dotenv.set_key(dotenv.find_dotenv(), PICKLE_PATH_ENV, path_pickle)
    else:
        Log.error(f"Invalid PICKLE_PATH: {path_pickle}")

    return True


if __name__ == "__main__":
    dotenv.load_dotenv(dotenv.find_dotenv())
    app_name = os.getenv(APP_NAME_ENV)
    Log.info(f"Installing {app_name}")
    install_internals_paths()

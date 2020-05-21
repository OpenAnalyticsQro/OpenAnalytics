import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from GoogleApi import GOOGLE_AUTH_SCOPES, TOKEN_CRED_PICKLE, GOOGLE_CRED_JSON
from Logger import authLogger as Log
from CommonOA import PICKLE_PATH_ENV, CREDENTIALS_PATH_ENV
import dotenv


def authorization_request(scopes=None):
    """ process the authorization process """
    if scopes is None:
        Log.error("Invalid scopes.")
        return None

    dotenv.load_dotenv(dotenv.find_dotenv())
    # Validating Credential Json
    path_cred = os.path.join(os.getenv(CREDENTIALS_PATH_ENV), GOOGLE_CRED_JSON)
    if os.path.isfile(path_cred) is False:
        Log.error(f"Invalid google_client_credentials.json: {path_cred}")
        return None

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_cred_path = os.path.join(os.getenv(PICKLE_PATH_ENV), TOKEN_CRED_PICKLE)
    Log.debug(f"Reading TOKEN_CRED_PICKLE: {token_cred_path}")
    if os.path.exists(token_cred_path):
        with open(token_cred_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            Log.info("Refreshing Token Credentials Pickle")
            creds.refresh(Request())
        else:
            Log.info("Generating Token Credentials Pickle")
            flow = InstalledAppFlow.from_client_secrets_file(
                path_cred, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_cred_path, 'wb') as token:
            Log.info(f"Saving token_cred.pickle in {token_cred_path}")
            pickle.dump(creds, token)

    Log.info("Authorization request process is completed.")
    return creds


if __name__ == "__main__":
    authorization_request(scopes=GOOGLE_AUTH_SCOPES)

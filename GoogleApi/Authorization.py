import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from GoogleApi import GOOGLE_AUTH_SCOPES
from Logger import authLogger as Log


def authorization_request(scopes=None, secret_cred=None):
    """ process the authorization process """
    if scopes is None:
        Log.error("Invalid scopes.")
        return None
    if secret_cred is None:
        Log.error("Invalid secret_cred.")
        return None

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secret_cred, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    Log.info("Authorization request process is completed.")
    return creds


if __name__ == "__main__":
    authorization_request(scopes=GOOGLE_AUTH_SCOPES, secret_cred="google_client_credentials.json")

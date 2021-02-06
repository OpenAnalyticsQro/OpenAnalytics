import os
import pickle
from OpenAnalytics.GoogleApi import google_api_log as log
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from OpenAnalytics.GoogleApi import GOOGLE_AUTH_SCOPES
from OpenAnalytics.GoogleApi.Credentials import GOOGLE_CRED_PATH_FILE
from OpenAnalytics.GoogleApi.Pickle import GOOGLE_PICK_FILE_PATH


def authorization_request(scopes=None):
    """ process the authorization process """
    if scopes is None:
        log.error("AuthAPi- Invalid scopes.")
        return None

    if GOOGLE_CRED_PATH_FILE.exists() is False:
        log.error(f"Invalid google_client_credentials.json: {GOOGLE_CRED_PATH_FILE}")
        return None

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if GOOGLE_PICK_FILE_PATH.exists():
        log.info(f"Reading TOKEN_CRED_PICKLE: {GOOGLE_PICK_FILE_PATH}")
        with open(GOOGLE_PICK_FILE_PATH, "rb") as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("Refreshing Token Credentials Pickle")
            creds.refresh(Request())
        else:
            log.info("Generating Token Credentials Pickle")
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CRED_PATH_FILE, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(GOOGLE_PICK_FILE_PATH, "wb") as token:
            log.info(f"Saving token_cred.pickle in {GOOGLE_PICK_FILE_PATH}")
            pickle.dump(creds, token)

    log.info("Authorization request process is completed.")
    return creds


if __name__ == "__main__":
    authorization_request(scopes=GOOGLE_AUTH_SCOPES)

from OpenAnalytics.GoogleApi import GOOGLE_AUTH_SCOPES
from OpenAnalytics.GoogleApi.AuthApi import authorization_request
from googleapiclient.discovery import build
from OpenAnalytics.GoogleApi import google_api_log as log
from OpenAnalytics.GoogleApi.Contacts import PEOPLE_SERVICE_NAME, PEOPLE_SERVICE_NAME_VERSION, PersonFields, PeopleConnections
from googleapiclient import errors
import json

def update_contact_list():
    """ contact test """
    creds = authorization_request(scopes=GOOGLE_AUTH_SCOPES)
    if creds is None:
        log.error("Contact Api - invalid Credential (delete/reload credentials)")
        return None

    service = build(serviceName=PEOPLE_SERVICE_NAME, version=PEOPLE_SERVICE_NAME_VERSION, credentials=creds)

    try:
        contactList = (
            service.people()
            .connections()
            .list(resourceName="people/me", personFields=f"{PersonFields.names},{PersonFields.addresses},{PersonFields.phoneNumbers},{PersonFields.emailAddresses}")
            .execute()
        )
        # peopleListResp = respAuthConectionPeople.get_from_cloud(response=contactList)
        people_connections = PeopleConnections.get_from_cloud(response=contactList)
        log.debug(people_connections)
        log.debug("Contact List has been requested!")
    except errors.Error as e:
        log.error(f"ContactList Error: {e}")
        return None
    
    return None


if __name__ == "__main__":
    update_contact_list()
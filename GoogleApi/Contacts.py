from GoogleApi import GOOGLE_AUTH_SCOPES
from GoogleApi.Authorization import authorization_request
from googleapiclient.discovery import build
from Logger import ContactsLogger as Log
from GoogleApi import PEOPLE_SERVICE, PEOPLE_SERVICE_VERSION
from googleapiclient import errors
import json

# Define Macros
PERSON_FIELDS_EMAIL = "emailAddresses"
PERSON_FIELDS_NAMES = "names"
PERSON_FIELDS_PHONE = "phoneNumbers"

class respAuthConectionPeople(object):
    """ The response to a request for the authenticated user's connections """
    # actualizado por DB
    contactList = {}

    def __init__(
        self,
        connections=None,  # The list of people that the requestor is connected to.
        nextPageToken=None,  # A token, which can be sent as pageToken to retrieve the next page.
        nextSyncToken=None,  # A token, which can be sent as syncToken to retrieve changes since the last request.
        totalPeople=0,  # The total number of items in the list without pagination.
        totalItems=0,  # (deprecated)
    ):
        self.connections = connections
        self.nextPageToken = nextPageToken
        self.nextSyncToken = nextSyncToken
        self.totalItems = totalItems
        self.totalPeople = totalPeople
        # init functions
        self.read_conections()
    
    @classmethod
    def get_from_cloud(cls, response=None):
        """ from json """
        if response is None:
            Log.error("Invalid response in respAuthConectionPeople")
            return None

        eventList = cls(**response)
        return eventList
    
    def read_conections(self):
        """ read conections """
        if self.connections is None:
            return False
        Log.debug("Reading Conections")

        for person in self.connections:
            self.get_names(names=person.get(PERSON_FIELDS_NAMES))
            self.get_phone_numbers(phoneNumbers=person.get(PERSON_FIELDS_PHONE))
            self.get_email(emailAddresses=person.get(PERSON_FIELDS_EMAIL))
    
    def get_names(self, names=None):
        """ Person names fields """
        if names is None:
            return False
        
        Log.debug(f"Reading: {PERSON_FIELDS_NAMES}")
        person = names[0]
        typeContact = person.get("metadata").get("source").get("type")
        personId = person.get("metadata").get("source").get("id")
        displayName = person.get('displayName')
        
        # data base Part
        if self.contactList.get(personId) == None:
            self.contactList[personId] = {"displayName":displayName, "typeContact":typeContact}
            self.contactList[personId]["id"] = personId
        else:
            self.contactList[personId]["displayName"] = displayName
            self.contactList[personId]["typeContact"]  = typeContact
        return True
    
    def get_phone_numbers(self, phoneNumbers=None):
        """ get Phone numbers """
        if phoneNumbers is None:
            return False
        
        Log.debug(f"Reading: {PERSON_FIELDS_PHONE}")
        phone = phoneNumbers[0]
        typeContact = phone.get("metadata").get("source").get("type")
        personId = phone.get("metadata").get("source").get("id")
        canonicalForm = phone.get("canonicalForm")

        # data base part
        if self.contactList.get(personId) == None:
            self.contactList[personId] = {"phone":canonicalForm, "typeContact":typeContact}
            self.contactList[personId]["id"] = personId
        else:
            self.contactList[personId]["phone"] = canonicalForm
            self.contactList[personId]["typeContact"]  = typeContact

        return True
    
    def get_email(self, emailAddresses=None):
        """ get eamil numbers """
        if emailAddresses is None:
            return False
        
        Log.debug(f"Reading: {PERSON_FIELDS_EMAIL}")
        email = emailAddresses[0]
        typeContact = email.get("metadata").get("source").get("type")
        personId = email.get("metadata").get("source").get("id")
        value = email.get("value")

        # data base part
        if self.contactList.get(personId) == None:
            self.contactList[personId] = {"email":value, "typeContact":typeContact}
        else:
            self.contactList[personId]["email"] = value
            self.contactList[personId]["typeContact"]  = typeContact

        return True


    def __str__(self):
        if self.connections is None:
            conections_str = "None"
        else:
            conections_str = "{...}"
        txt = "\n# The response to a request for the authenticated user's connections.\n"
        txt += f" -totalPeople:{self.totalPeople}\n -nextPageToken:{self.nextPageToken}\n -nextSyncToken:{self.nextSyncToken}\n -connections:{conections_str}"
        return txt



def update_contact_list():
    """ contact test """
    creds = authorization_request(scopes=GOOGLE_AUTH_SCOPES)
    if creds is None:
        Log.error("update_contact_list(): invalid autorizartion request")
        return None

    service = build(PEOPLE_SERVICE, PEOPLE_SERVICE_VERSION, credentials=creds)

    try:
        contactList = (
            service.people()
            .connections()
            .list(resourceName="people/me", personFields="names,phoneNumbers,emailAddresses")
            .execute()
        )
        peopleListResp = respAuthConectionPeople.get_from_cloud(response=contactList)
        # Log.debug(str(peopleListResp))
        # print(peopleListResp.contactList)
        # print(json.dumps(peopleListResp.contactList))
        Log.info("Contact List has been updated!")
    except Exception as e:
        Log.error("There was an error in People.Conections.list():")
        Log.error(e)
        return None
    # return json.dumps(peopleListResp.contactList)
    data = [peopleListResp.contactList[e] for e in peopleListResp.contactList]
    # print(json.dumps(data))
    return json.dumps(data)


if __name__ == "__main__":
    # calendar_event_list()
    # calendar_send_event()
    update_contact_list()

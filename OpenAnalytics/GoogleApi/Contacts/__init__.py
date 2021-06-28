# ref: https://developers.google.com/people/api

from OpenAnalytics.GoogleApi import google_api_log as log

# Define Contacts Group
PEOPLE_SERVICE_NAME = "people"
PEOPLE_SERVICE_NAME_VERSION = "v1"

# MACROS
class PersonFields(object):
    addresses = "addresses"
    ageRanges = "ageRanges"
    biographies = "biographies"
    birthdays = "birthdays"
    calendarUrls = "calendarUrls"
    clientData = "clientData"
    coverPhotos = "coverPhotos"
    emailAddresses = "emailAddresses"
    events = "events"
    externalIds = "externalIds"
    genders = "genders"
    imClients = "imClients"
    interests = "interests"
    locales = "locales"
    locations = "locations"
    memberships = "memberships"
    metadata = "metadata"
    miscKeywords = "miscKeywords"
    names = "names"
    nicknames = "nicknames"
    occupations = "occupations"
    organizations = "organizations"
    phoneNumbers = "phoneNumbers"
    photos = "photos"
    relations = "relations"
    sipAddresses = "sipAddresses"
    skills = "skills"
    urls = "urls"
    userDefined = "userDefined"


# CLASES
class ContactsPersonEmail(object):
    def __init__(
        self, metadata=None, value=None, formattedType=None, displayName=None, type=None
    ):
        # self.metadata = metadata
        self.value = value
        # self.type = type
        # self.formattedType = formattedType
        # self.displayName = displayName

    @classmethod
    def get_from_cloud(cls, response=None):
        """ from json """
        if response is None:
            log.error("Invalid response in ContactsPersonEmail")
            return None
        return cls(**response)

    def __str__(self):
        if self.value is not None:
            return f"e-mail: {self.value}"


class ContactsPersonName(object):
    def __init__(
        self,
        metadata=None,
        displayName=None,
        displayNameLastFirst=None,
        unstructuredName=None,
        familyName=None,
        givenName=None,
        middleName=None,
        honorificPrefix=None,
        honorificSuffix=None,
        phoneticFullName=None,
        phoneticFamilyName=None,
        phoneticGivenName=None,
        phoneticMiddleName=None,
        phoneticHonorificPrefix=None,
        phoneticHonorificSuffix=None,
    ):
        # self.metadata
        self.displayName = displayName
        self.displayNameLastFirst = displayNameLastFirst
        # self.unstructuredName
        self.familyName = familyName
        self.givenName = givenName
        self.middleName = middleName
        # self.honorificPrefix
        # self.honorificSuffix
        # self.phoneticFullName
        # self.phoneticFamilyName
        # self.phoneticGivenName
        # self.phoneticMiddleName
        # self.phoneticHonorificPrefix
        # self.phoneticHonorificSuffix
    
    @classmethod
    def get_from_cloud(cls, response=None):
        """ from json """
        if response is None:
            log.error("Invalid response in ContactsPersonName")
            return None
        return cls(**response)
    
    def __str__(self):
        return f"{self.displayName}"


class ContactsPerson(object):
    def __init__(
        self,
        resourceName=None,
        etag=None,
        metadata=None,
        addresses=None,
        ageRange=None,
        ageRanges=None,
        biographies=None,
        birthdays=None,
        braggingRights=None,
        calendarUrls=None,
        clientData=None,
        coverPhotos=None,
        emailAddresses=None,
        events=None,
        externalIds=None,
        fileAses=None,
        genders=None,
        imClients=None,
        interests=None,
        locales=None,
        locations=None,
        memberships=None,
        miscKeywords=None,
        names=None,
        nicknames=None,
        occupations=None,
        organizations=None,
        phoneNumbers=None,
        photos=None,
        relations=None,
        relationshipInterests=None,
        relationshipStatuses=None,
        residences=None,
        sipAddresses=None,
        skills=None,
        taglines=None,
        urls=None,
        userDefined=None,
    ):
        self.resourceName = resourceName
        self.etag = etag  # Not used
        self.metadata = metadata  # Not used
        self.addresses = addresses
        self.ageRanges = ageRanges
        self.biographies = biographies  # Not Used
        self.birthdays = birthdays  # Not Used
        self.calendarUrls = calendarUrls  # Not Used
        self.clientData = clientData  # Not Used
        self.coverPhotos = coverPhotos
        self.emailAddresses = self.get_email_adresses(list_adresses=emailAddresses)
        self.events = events  # Not Used
        self.externalIds = externalIds  # Not Used
        self.fileAses = fileAses  # Not Used
        self.genders = genders  # Not Used
        self.imClients = imClients  # Not Used
        self.interests = interests  # Not Used
        self.locales = locales  # Not Used
        self.locations = locations  # Not Used
        self.memberships = memberships  # Not Used
        self.miscKeywords = miscKeywords  # Not Used
        self.names = self.get_names(list_names=names)
        self.nicknames = nicknames  # Not Used
        self.occupations = occupations  # Not Used
        self.organizations = organizations  # Not Used
        self.phoneNumbers = phoneNumbers
        self.photos = photos
        self.relations = relations
        self.relationshipInterests = relationshipInterests
        self.relationshipStatuses = relationshipStatuses
        self.residences = residences
        self.sipAddresses = sipAddresses
        self.skills = skills
        self.taglines = taglines
        self.urls = urls
        self.userDefined = userDefined

    def get_email_adresses(self, list_adresses=None):
        if isinstance(list_adresses, list) is False:
            return None
        buf = []
        for email in list_adresses:
            buf.append(ContactsPersonEmail.get_from_cloud(response=email))
        return buf
    
    def get_names(self, list_names=None):
        if isinstance(list_names, list) is False:
            return None
        return ContactsPersonName.get_from_cloud(response=list_names[0])

    @classmethod
    def get_from_cloud(cls, response=None):
        """ from json """
        if response is None:
            log.error("Invalid response in respAuthConectionPeople")
            return None
        contacts_people = cls(**response)
        return contacts_people

    def __str__(self):
        data = ""
        data += f"{self.names}\n"
        data += f"{self.resourceName}\n"
        for email in self.emailAddresses:
            data += f"{email}\n"
        return data


class PeopleConnections(object):
    def __init__(
        self,
        connections=None,
        nextPageToken=None,
        nextSyncToken=None,
        totalPeople=None,
        totalItems=None,
    ):
        self.connections = []
        self.nextPageToken = nextPageToken
        self.nextSyncToken = nextSyncToken
        self.totalPeople = totalPeople
        self.totalItems = totalItems
        self.get_connections(connections=connections)

    def get_connections(self, connections=None):
        if connections is not None:
            for people in connections:
                person = ContactsPerson.get_from_cloud(response=people)
                print(person)
                # print (person.names)
                # print(person.phoneNumbers)
                # print(person.emailAddresses)

    @classmethod
    def get_from_cloud(cls, response=None):
        """ from json """
        if response is None:
            log.error("Invalid response in respAuthConectionPeople")
            return None

        contacts_people_conection = cls(**response)
        return contacts_people_conection

    def __str__(self):
        return f"PeopleConnectionsListResponse- TotalPeople:{self.totalPeople} TotalItems: {self.totalItems} nextPage: {self.nextPageToken} nextSync: {self.nextSyncToken}"

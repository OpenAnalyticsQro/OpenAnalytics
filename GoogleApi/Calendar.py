from GoogleApi import GOOGLE_AUTH_SCOPES, CALENDAR_SERVICE, CALENDAR_SERVICE_VERSION
from GoogleApi.Authorization import authorization_request
from googleapiclient.discovery import build
from Logger import calendarLogger as Log
import datetime
from os import getenv
from CommonOA import LOCAL_TIME_ZONE
import dotenv
import inspect


# CALENDARS IDS
CALENDAR_EVENT = "calendar#event"
CALENDAR_EVENT_LIST = "calendar#events"

# TRANSPARENCY
CALENDAR_TRANSPARENCY_OPAQUE = "opaque"  # The event does block time on the calendar. This is equivalent to setting Show me as to Busy.
CALENDAR_TRANSPARENCY_TRANSPARENT = "transparent"  # The event does not block time on the calendar. This is equivalent to setting Show me as to Available.

# VISIBILITY
CALENDAR_VISIBILITY_DEFUALT = "default"  # Uses the default visibility for events on the calendar. This is the default value.
CALENDAR_VISIBILITY_PUBLIC = "public"  # The event is public and event details are visible to all readers of the calendar.
CALENDAR_VISIBILITY_PRIVATE = (
    "private"  # The event is private and only event attendees may view event details.
)
CALENDAR_VISIBILITY_CONFIDENTIAL = "confidential"  # The event is private. This value is provided for compatibility reasons.

# ATENDEER RESPONSE
CALENDAR_ATTENDEER_RESPONSE_NEEDS_ACTION = (
    "needsAction"  # The attendee has not responded to the invitation.
)
CALENDAR_ATTENDEER_RESPONSE_DECLINED = (
    "declined"  # The attendee has declined the invitation.
)
CALENDAR_ATTENDEER_RESPONSE_TENTATIVE = (
    "tentative"  # The attendee has tentatively accepted the invitation.
)
CALENDAR_ATTENDEER_RESPONSE_ACEPTED = (
    "accepted"  # The attendee has accepted the invitation.
)


class CalendarSource(object):
    """ Calendar Source """

    url = ""  # URL of the source pointing to a resource. The URL scheme must be HTTP or HTTPS.
    title = ""  # Title of the source; for example a title of a web page or an email subject.

    def __init__(self, json_file=None):
        if json_file is None:
            Log.error("Invalid Calendar Source")
        else:
            self.url = json_file.get("url")
            self.title = json_file.get("title")

    def __str__(self):
        """ str """
        txt = f"\n    url: {self.url}\n"
        txt += f"    title: {self.title}"
        return txt


class CalendarReminder(object):
    """ Reminder """

    # useDefault  - Whether the default reminders of the calendar apply to the event.
    # overrides  - The method used by this reminder.

    def __init__(self, useDefault=False, overrides=[]):
        self.useDefault = useDefault
        self.overrides = overrides

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is None:
            Log.error("Invalid Calendar Reminder")
            return None
        return cls(**json_dict)

    def __str__(self):
        """ str """
        txt = f"\n    useDefault: {self.useDefault}\n"
        txt += f"    overrides: {self.overrides}"
        return txt


class CalendarCreator(object):
    """ creator Calendar """

    # id  - he creator's Profile ID, if available. It corresponds to the id field in the People collection of the Google+ API
    # email  - The creator's email address, if available.
    # displayName  - The creator's name, if available.
    # self_creator  - Whether the creator corresponds to the calendar on which this copy of the event appears. Read-only. The default is False.

    def __init__(self, id=None, email=None, displayName=None, self_creator=False):
        self.id = id
        self.email = email
        self.displayName = displayName
        self.self_creator = self_creator

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is None:
            Log.error("Invalid Calendar Creator")
            return None
        if json_dict.get("self") is not None:
            json_dict["self_creator"] = json_dict.pop("self")
        return cls(**json_dict)

    def __str__(self):
        """ str """
        txt = f"\n    id: {self.id}\n"
        txt += f"    email: {self.email}\n"
        txt += f"    displayName: {self.displayName}\n"
        txt += f"    self_creator: {self.self_creator}"
        return txt


class CalendarOrganizer(object):
    """ organizer Calendar """

    # id  - The organizer's Profile ID, if available. It corresponds to the id field in the People collection of the Google+ API
    # email  - The organizer's email address, if available.
    # displayName  - The organizer's name, if available.
    # self_organizer  - Whether the organizer corresponds to the calendar on which this copy of the event appears. Read-only. The default is False.

    def __init__(self, id=None, email=None, displayName=None, self_organizer=None):
        self.id = id
        self.email = email
        self.displayName = displayName
        self.self_organizer = self_organizer

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is None:
            Log.error("Invalid Calendar Organizer")
            return None
        if json_dict.get("self") is not None:
            json_dict["self_organizer"] = json_dict.pop("self")
        return cls(**json_dict)

    def __str__(self):
        """ str """
        txt = f"\n    id: {self.id}\n"
        txt += f"    email: {self.email}\n"
        txt += f"    displayName: {self.displayName}\n"
        txt += f"    self_creator: {self.self_organizer}"
        return txt


class CalendarDateTime(object):
    """ Calendar DateTime """

    date = None  # The date, in the format "yyyy-mm-dd", if this is an all-day event.
    dateTime = None  # The time zone in which the time is specified. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".)
    timeZone = ""  # A time zone offset is required unless a time zone is explicitly specified in timeZone.

    def __init__(self, date=None, dateTime=None, timeZone=None):
        self.date = date
        self.dateTime = dateTime
        self.timeZone = timeZone

    def set_time(self, year=2020, day=1, month=1, hour=1, minute=0):
        """ set time """
        time = datetime.datetime(
            year=year, day=day, month=month, hour=hour, minute=minute
        )
        self.dateTime = time.isoformat("T")

    def date_time_to_json(self):
        """ date time to json """
        time_json = {}

        if self.date is not None:
            time_json["date"] = self.date

        if self.dateTime is not None:
            time_json["dateTime"] = self.dateTime

        # if self.timeZone != "":
        time_json["timeZone"] = getenv(LOCAL_TIME_ZONE)  # Hirvin

        return time_json

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is None:
            Log.error("Invalid Calendar Date Time")
            return None
        return cls(**json_dict)

    def __str__(self):
        """ str """
        txt = f"\n    date: {self.date}\n"
        txt += f"    datetime: {self.dateTime}\n"
        txt += f"    timeZone: {self.timeZone}"
        return txt


class CalendarAttendeer(object):
    """ Calendar Ateender """

    # id - The attendee's Profile ID, if available. It corresponds to the id field in the People collection of the Google+ API
    # email - The attendee's email address, if available.
    # displayName - The attendee's name, if available. Optional.
    # organizer - Whether the attendee is the organizer of the event. Read-only. The default is False.
    # self_atender - Whether this entry represents the calendar on which this copy of the event appears. Read-only. The default is False.
    # resource - Whether the attendee is a resource. Can only be set when the attendee is added to the event for the first time.
    # optional - Whether this is an optional attendee. Optional. The default is False.
    # responseStatus - The attendee's response status.
    # comment - The attendee's response comment. Optional.
    # additionalGuests - Number of additional guests. Optional. The default is 0.

    def __init__(
        self,
        id=None,
        email=None,
        displayName=None,
        organizer=False,
        self_atender=None,
        resource=False,
        optional=False,
        responseStatus=CALENDAR_ATTENDEER_RESPONSE_NEEDS_ACTION,
        comment=None,
        additionalGuests=0,
    ):
        self.id = id
        self.email = email
        self.displayName = displayName
        self.organizer = organizer
        self.self_atender = self_atender
        self.resource = resource
        self.optional = optional
        self.responseStatus = responseStatus
        self.comment = comment
        self.additionalGuests = additionalGuests

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is None:
            Log.error("Invalid Calendar Attendeer")
            return None

        if json_dict.get("self") is not None:
            json_dict["self_atender"] = json_dict.pop("self")
        return cls(**json_dict)

    def __str__(self):
        """ str """
        txt = "Attendeer:\n"
        txt += f"    id: {self.id}\n"
        txt += f"    email: {self.email}\n"
        txt += f"    displayName: {self.displayName}\n"
        txt += f"    organizer: {self.organizer}\n"
        txt += f"    self_atender: {self.self_atender}\n"
        txt += f"    resource: {self.resource}\n"
        txt += f"    optional: {self.optional}\n"
        txt += f"    responseStatus: {self.responseStatus}\n"
        txt += f"    comment: {self.comment}\n"
        txt += f"    additionalGuests: {self.additionalGuests}"
        return txt


class CalendarEventList(object):
    """ Calendar Event List """

    # kind - Type of the resource ("calendar#event").
    # etag - ETag of the resource
    # summary - Title of the event.
    # description -  Description of the event. Can contain HTML. Optional.
    # updated - datetime  Last modification time of the event (as a RFC3339 timestamp). Read-only.
    # timeZone - The time zone of the calendar. Read-only.
    # accessRole - none - The user has no access.
    #            - freeBusyReader - The user has read access to free/busy information.
    #            - reader - The user has read access to the calendar. Private events will appear to users with reader access, but event details will be hidden.
    #            - writer - The user has read and write access to the calendar. Private events will appear to users with writer access, and event details will be visible.
    #            - owner - The user has ownership of the calendar. This role has all of the permissions of the writer role with the additional ability to see and manipulate ACLs.
    # defaultReminders - he default reminders on the calendar for the authenticated user.
    # nextPageToken - Token used to access the next page of this result.
    # nextSyncToken - Token used at a later point in time to retrieve only the entries that have changed since this result was returned.
    # items - List of events on the calendar.
    def __init__(
        self,
        kind=None,
        etag=None,
        summary=None,
        description=None,
        updated=None,
        timeZone=None,
        accessRole=None,
        defaultReminders=[],
        nextPageToken=None,
        nextSyncToken=None,
        items=[],
    ):
        self.kind = kind
        self.etag = etag
        self.summary = summary
        self.description = description
        self.updated = updated
        self.timeZone = timeZone
        self.accessRole = accessRole
        self.defaultReminders = defaultReminders
        self.nextPageToken = nextPageToken
        self.nextSyncToken = nextSyncToken
        self.items = items

    @classmethod
    def get_from_cloud(cls, service=None, calendarId=None, page_token=None):
        """ from json """
        if service is None:
            Log.error("Invalid service in CalendarEventList")
            return None
        if calendarId is None:
            Log.error("Invalid CalendarId in CalendarEventList")
            return None

        Log.info(f"Generating CalendarEventList from cloud, CalendarId:{calendarId} pageToke:{page_token}")
        events_list = service.events().list(calendarId=calendarId, pageToken=page_token).execute()
        if CALENDAR_EVENT_LIST != events_list["kind"]:
            return None

        eventList = cls(**events_list)
        events = []
        for event in eventList.items:
            events.append(CalendarEvent.from_json(event))
        eventList.items = events

        return eventList

    def __str__(self):
        txt = f"\n{'#'*40}\n# {self.kind} {self.etag}\n{'#'*40}\n"
        for element in inspect.getmembers(self):
            if not element[0].startswith('_'):
                if not inspect.ismethod(element[1]):
                    # if not inspect.isclass(element[])
                    txt += f"{element[0]}: {element[1]}\n"
        return txt


class CalendarEvent(object):
    """ Calenda Event """

    # kind - Type of the resource ("calendar#event").
    # etag - ETag of the resource
    # id - ID event, If you do not specify an ID, it will be automatically generated by the server
    # status - Status of the event. Optional. Possible values are: confirmed, tentative and cancelled
    # htmlLink - An absolute link to this event in the Google Calendar Web UI. Read-only.
    # created - datetime. Creation time of the event (as a RFC3339 timestamp). Read-only.
    # updated - datetime  Last modification time of the event (as a RFC3339 timestamp). Read-only.
    # summary - Title of the event.
    # description -  Description of the event. Can contain HTML. Optional.
    # location -  Geographic location of the event as free-form text. Optional.
    # colorId -  The color of the event. This is an ID referring to an entry in the event section of the colors definition
    # creator -  The creator of the event. Read-only.
    # organizer -  The organizer of the event.
    # start - The (inclusive) start time of the event. For a recurring event, this is the start time of the first instance.
    # end - The (exclusive) end time of the event. For a recurring event, this is the end time of the first instance.
    # endTimeUnspecified - Whether the end time is actually unspecified. An end time is still provided for compatibility reasons.
    # recurrence -  not supported
    # recurringEventId  - For an instance of a recurring event, this is the id of the recurring event to which this instance belongs. Immutable.
    # originalStartTime - start according to the recurrence data in the recurring event identified by recurringEventId.
    # transparency - Whether the event blocks time on the calendar. see CALENDAR TRANSPARENCY OPTIONS
    # visibility - Visibility of the event. see CALENDAR_VISIBILITY_OPTIONS
    # iCalUID - It is used to uniquely identify events accross calendaring systems and must be supplied when importing events via the import method.
    # sequence - Sequence number as per iCalendar.
    # attendees - The attendees of the event. See the Events with attendees guide for more information on scheduling events with other calendar users.
    # attendeesOmitted - When updating an event, this can be used to only update the participant's response. Optional. The default is False.
    # extendedProperties - Not supported
    # hangoutLink - Not supported
    # conferenceData - Not supported
    # anyoneCanAddSelf - Whether anyone can invite themselves to the event (currently works for Google+ events only). Optional. The default is False.
    # guestsCanInviteOthers - Whether attendees other than the organizer can invite others to the event. Optional.
    # guestsCanModify - Whether attendees other than the organizer can modify the event. Optional.
    # guestsCanSeeOtherGuests - Whether attendees other than the organizer can see who the event's attendees are.
    # privateCopy - If set to True, Event propagation is disabled. Note that it is not the same thing as Private event properties.
    # locked - Whether this is a locked event copy where no changes can be made to the main event fields "summary", "description", "location", "start", "end" or "recurrence.
    # reminders - Information about the event's reminders for the authenticated user.
    # source - Source from which the event was created.
    # attachments - Not supported

    def __init__(
        self,
        kind=None,
        etag=None,
        id=None,
        status=None,
        htmlLink=None,
        created=None,
        updated=None,
        summary=None,
        description=None,
        location=None,
        colorId=None,
        creator=None,
        organizer=None,
        start=None,
        end=None,
        endTimeUnspecified=False,
        recurrence="Not Supported",
        recurringEventId=None,
        originalStartTime=None,
        transparency=CALENDAR_TRANSPARENCY_OPAQUE,
        visibility=CALENDAR_VISIBILITY_DEFUALT,
        iCalUID=None,
        sequence=0,
        attendees=[],
        attendeesOmitted=False,
        extendedProperties=None,
        hangoutLink="Not Supported",
        conferenceData="Not Supported",
        anyoneCanAddSelf=False,
        guestsCanInviteOthers=False,
        guestsCanModify=False,
        guestsCanSeeOtherGuests=False,
        privateCopy=False,
        locked=False,
        reminders=None,
        source=None,
        attachments=None,
        fromJson=False,
    ):
        if fromJson is False:
            Log.info("Creating Calendar Event")
        self.kind = kind
        self.etag = etag
        self.id = id
        self.status = status
        self.htmlLink = htmlLink
        self.created = created
        self.updated = updated
        self.summary = summary
        self.description = description
        self.location = location
        self.colorId = colorId
        self.creator = CalendarCreator.from_json(creator)
        self.organizer = CalendarOrganizer.from_json(organizer)
        self.start = CalendarDateTime.from_json(start)
        self.end = CalendarDateTime.from_json(end)
        self.endTimeUnspecified = endTimeUnspecified
        self.recurrence = recurrence
        self.recurringEventId = recurringEventId
        self.originalStartTime = originalStartTime
        self.transparency = transparency
        self.visibility = visibility
        self.iCalUID = iCalUID
        self.sequence = sequence
        self.attendeesOmitted = attendeesOmitted
        self.extendedProperties = extendedProperties
        self.hangoutLink = hangoutLink
        self.conferenceData = conferenceData
        self.anyoneCanAddSelf = anyoneCanAddSelf
        self.guestsCanInviteOthers = guestsCanInviteOthers
        self.guestsCanModify = guestsCanModify
        self.guestsCanSeeOtherGuests = guestsCanSeeOtherGuests
        self.privateCopy = False
        self.locked = locked
        self.reminders = CalendarReminder.from_json(reminders)
        self.source = source
        self.attachments = attachments

        self.attendees = []
        for attender in attendees:
            self.attendees.append(CalendarAttendeer.from_json(attender))

    @classmethod
    def from_json(cls, json_dict):
        """ from json """
        if json_dict is not None:
            if json_dict["kind"] == CALENDAR_EVENT:
                Log.info("Creating event from json dict.")
            else:
                Log.error("Invalide Calendar Event ID")
                return None
        else:
            Log.error("Invalid Calendar Dictionary")
            return None
        json_dict["fromJson"] = True
        return cls(**json_dict)

    def init_empty_event(self):
        """ init event """
        self.start = CalendarDateTime()
        self.end = CalendarDateTime()

    def calendar_get_attendees(self, json_file=None):
        """ get attendess """
        if json_file is None:
            Log.error("Invalid Calendar Attendees")
            return []

        attendeer_list = []
        for attendeer in json_file:
            attendeer_list.append(CalendarAttendeer(attendeer))
        return attendeer_list

    def event_to_json(self):
        """ event to json """
        event_json = {}
        event_json["summary"] = self.summary
        event_json["start"] = self.start.date_time_to_json()
        event_json["end"] = self.end.date_time_to_json()
        return event_json

    def __str__(self):
        """ str """
        txt = f"\n{'#'*40}\n# {self.kind} {self.etag}\n{'#'*40}\n"
        txt += f"kind: {self.kind}\n"
        txt += f"etag: {self.etag}\n"
        txt += f"id: {self.id}\n"
        txt += f"status: {self.status}\n"
        txt += f"htmlLink: {self.htmlLink}\n"
        txt += f"created: {self.created}\n"
        txt += f"updated: {self.updated}\n"
        txt += f"summary: {self.summary}\n"
        txt += f"description: {self.description}\n"
        txt += f"location: {self.location}\n"
        txt += f"colorId: {self.colorId}\n"
        txt += f"creator: {str(self.creator)}\n"
        txt += f"organizer: {str(self.organizer)}\n"
        txt += f"start: {str(self.start)}\n"
        txt += f"end: {str(self.end)}\n"
        txt += f"endTimeUnspecified: {self.endTimeUnspecified}\n"
        txt += f"recurrence: {self.recurrence}\n"
        txt += f"recurringEventId: {self.recurringEventId}\n"
        txt += f"originalStartTime: {str(self.originalStartTime)}\n"
        txt += f"transparency: {self.transparency}\n"
        txt += f"visibility: {self.visibility}\n"
        txt += f"iCalUID: {self.iCalUID}\n"
        txt += f"sequence: {self.sequence}\n"
        txt += f"attendeesOmitted: {self.attendeesOmitted}\n"
        txt += f"extendedProperties: {self.extendedProperties}\n"
        txt += f"hangoutLink: {self.hangoutLink}\n"
        txt += f"conferenceData: {self.conferenceData}\n"
        txt += f"anyoneCanAddSelf: {self.anyoneCanAddSelf}\n"
        txt += f"guestsCanInviteOthers: {self.guestsCanInviteOthers}\n"
        txt += f"guestsCanModify: {self.guestsCanModify}\n"
        txt += f"guestsCanSeeOtherGuests: {self.guestsCanSeeOtherGuests}\n"
        txt += f"privateCopy: {self.privateCopy}\n"
        txt += f"locked: {self.locked}\n"
        txt += f"reminders: {str(self.reminders)}\n"
        txt += f"source: {str(self.source)}\n"
        txt += f"attachments: {self.attachments}\n"
        for attendeer in self.attendees:
            txt += f"{str(attendeer)}\n"
        return txt


def calendar_event_list():
    """ return calendar event list """
    creds = authorization_request(scopes=GOOGLE_AUTH_SCOPES)
    service = build(CALENDAR_SERVICE, CALENDAR_SERVICE_VERSION, credentials=creds)

    while True:
        eventList = CalendarEventList.get_from_cloud(service=service, calendarId="primary", page_token=None)
        print(eventList)

        for item in eventList.items:
            print(item)

        if not eventList.nextPageToken:
            break


eventCalendar = {
  'summary': 'Test Event',
  'description': 'Test event',
  'start': {
    'dateTime': '2020-06-16T17:00:00-00:00',
    'timeZone': 'America/Mexico_City',
  },
  'end': {
    'dateTime': '2020-06-16T17:30:00-00:00',
    'timeZone': 'America/Mexico_City',
  },
}

def calendar_send_event(day=14):
    """ send event """
    # event = CalendarEvent()
    # event.summary = "Prueba desde compu"
    # event.start.set_time(year=2020, day=14, month=6, hour=18, minute=0)
    # event.end.set_time(year=2020, day=14, month=6, hour=18, minute=30)
    # Log.info(event.event_to_json())

    creds = authorization_request(scopes=GOOGLE_AUTH_SCOPES)
    service = build(CALENDAR_SERVICE, CALENDAR_SERVICE_VERSION, credentials=creds)
    # service.events().insert(calendarId="primary", body=event.event_to_json()).execute()
    service.events().insert(calendarId="primary", body=eventCalendar).execute()


if __name__ == "__main__":
    # calendar_event_list()
    calendar_send_event()
    # contacts_test()


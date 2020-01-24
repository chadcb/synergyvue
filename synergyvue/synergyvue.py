import datetime
import logging
import xml.etree.ElementTree as ET
from zeep import Client

# Suppress Message:  Forcing soap:address location to HTTPS
# https://stackoverflow.com/questions/58662933/zeep-disable-warning-forcing-soapaddress-location-to-https
logging.getLogger("zeep").setLevel(logging.ERROR)


class StudentVUE:
    """Class for handing connectivity to StudentVUE.

    StudentVUE is a product of Edupoint
    http://www.edupoint.com/Products/ParentVUE-StudentVUE
    """

    def __init__(self, user, password, host, message_limit=5):
        self._user = user
        self._password = password
        self._synergyvue_host = host
        self._synergyvue_url = (
            f"https://{self._synergyvue_host}/Service/PXPCommunication.asmx?WSDL"
        )
        self._xml_client = None
        self._last_updated = datetime.datetime.now().isoformat()

        self._recent_message_limit = message_limit

        # Stored xml data returned from each request
        self._grade_book_xml = None
        self._child_list_xml = None
        self._pxp_messages_xml = None

        # XML Roots
        self._child_list_xml_root = None

        # Child data parsed from xml
        self._reporting_period = {}
        self._courses = {}
        self._child_attribs = {}
        self._messages = {}

        # Calculated data
        self._gpa = 0
        self._na_marks = 0
        self._course_count = 0
        self._raw_grade_total = 0
        self._missing_assignments = 0

        # Params for each of the queries needed to popluate all of the data
        self._grade_book_params = {
            "userID": self._user,
            "password": self._password,
            "skipLoginLog": "0",
            "parent": "0",
            "webServiceHandleName": "PXPWebServices",
            "methodName": "Gradebook",
            "paramStr": "<Parms><ChildIntId>0</ChildIntId></Parms>",
        }

        self._get_content_user_defined_module_params = {
            "userID": self._user,
            "password": self._password,
            "skipLoginLog": "0",
            "parent": "0",
            "webServiceHandleName": "PXPWebServices",
            "methodName": "GetContentUserDefinedModule",
            "paramStr": "<Parms><ChildIntId>0</ChildIntId></Parms>",
        }

        self._get_pxp_messages_params = {
            "userID": self._user,
            "password": self._password,
            "skipLoginLog": "0",
            "parent": "0",
            "webServiceHandleName": "PXPWebServices",
            "methodName": "GetPXPMessages",
            "paramStr": "<Parms><ChildIntId>0</ChildIntId></Parms>",
        }

        self._child_list_params = {
            "userID": self._user,
            "password": self._password,
            "skipLoginLog": "0",
            "parent": "0",
            "webServiceHandleName": "PXPWebServices",
            "methodName": "ChildList",
            "paramStr": "<Parms></Parms>",
        }

        # Connect and gather all xml data. If we can't do this, then bail as nothing more to do...
        # TODO: Not working as expected. Need to handle username/password issues within Zeep requests also
        try:
            self._xml_client = Client(self._synergyvue_url)
            self._grade_book_xml = self._xml_client.service.ProcessWebServiceRequest(
                **self._grade_book_params
            )
            self._child_list_xml = self._xml_client.service.ProcessWebServiceRequest(
                **self._child_list_params
            )
            self._pxp_messages_xml = self._xml_client.service.ProcessWebServiceRequest(
                **self._get_pxp_messages_params
            )
            self._child_list_xml_root = ET.fromstring(self._child_list_xml)
        except:
            # TODO: How to gracefully bail?
            print(f"Error connecting to: {self._synergyvue_url}")
            exit()

        # If we got here, populate data
        self._get_reporting_period()
        self._get_child_attribs()
        self._get_courses()
        self._get_messages()

    def _get_child_attribs(self):
        """Populate the child attributes."""
        for child_el in self._child_list_xml_root.iter("Child"):
            self._child_attribs["rotation_code"] = child_el.attrib["RotationCode"]
            self._child_attribs["child_first_name"] = child_el.attrib["ChildFirstName"]
            self._child_attribs["child_perm_id"] = child_el.attrib["ChildPermID"]
        return

    def _get_courses(self):
        """Iterate through courses and populate course dict."""
        xml_root_courses = ET.fromstring(self._grade_book_xml)
        for course in xml_root_courses.iter("Course"):
            try:
                course_title, course_id = course.attrib["Title"].split(" (")
                course_id = course_id.split(")")[0]
            except:
                course_title = f"{course.attrib['Title']}"
                course_id = None
            if course_title not in self._courses:
                self._courses[course_title] = {}
                self._courses[course_title]["course_id"] = course_id
                self._courses[course_title]["period"] = course.attrib["Period"]
                self._courses[course_title]["room"] = course.attrib["Room"]
                self._courses[course_title]["staff"] = course.attrib["Staff"]
                self._courses[course_title]["staff_email"] = course.attrib["StaffEMail"]
                for mark in course.iter("Mark"):
                    self._courses[course_title]["mark_name"] = mark.attrib["MarkName"]
                    self._courses[course_title]["grade_letter"] = mark.attrib[
                        "CalculatedScoreString"
                    ]
                    self._courses[course_title]["grade_raw"] = mark.attrib[
                        "CalculatedScoreRaw"
                    ]
                    self._courses[course_title]["missing_assignments"] = 0
                    self._raw_grade_total += int(mark.attrib["CalculatedScoreRaw"])
                    if "N/A" in mark.attrib["CalculatedScoreString"]:
                        self._na_marks += 1
                    for assignment in mark.iter("Assignment"):
                        if "Missing" in assignment.attrib["Notes"]:
                            self._courses[course_title]["missing_assignments"] += 1
                            self._missing_assignments += 1
                self._course_count += 1
        return

    def _get_messages(self):
        """Iterate through message list and populate message dict."""
        message_id = None
        for message in ET.fromstring(self._pxp_messages_xml).find("MessageListings"):
            message_id = message.attrib["ID"]
            if message_id in self._messages:
                continue
            self._messages[message_id] = message.attrib
        return

    def _get_reporting_period(self):
        """Get reporting period attributes, Quarter, start and end dates."""
        xml_root_gradebook = ET.fromstring(self._grade_book_xml)
        reporting_period = xml_root_gradebook.find("ReportingPeriod")
        self._reporting_period["grade_period"] = reporting_period.attrib["GradePeriod"]
        self._reporting_period["start_date"] = reporting_period.attrib["StartDate"]
        self._reporting_period["end_date"] = reporting_period.attrib["EndDate"]
        return

    @property
    def url(self):
        """Return full URL used for API calls to SynergyVUE."""
        return self._synergyvue_url

    @property
    def courses(self):
        """Return course dict."""
        return self._courses

    @property
    def meeting_date(self):
        """Return meeting date, also known in our area as x/y day for alternate classes."""
        try:
            return (
                self._child_attribs["rotation_code"]
                .split("Date:")[1]
                .split(" Meeting Day")[0]
            )
        except:
            return None

    @property
    def meeting_day(self):
        """Return meeting day, also known in our area as x/y day for alternate classes."""
        try:
            return self._child_attribs["rotation_code"].split("Meeting Day:")[1]
        except:
            return None

    @property
    def id(self):
        """Return student ID."""
        return self._child_attribs["child_perm_id"]

    @property
    def first_name(self):
        """Return first name."""
        return self._child_attribs["child_first_name"]

    @property
    def grade(self):
        """Return grade level."""
        return self._child_list_xml_root.find("Child").find("Grade").text

    @property
    def school_name(self):
        """Return the name of the school."""
        return self._child_list_xml_root.find("Child").find("OrganizationName").text

    @property
    def child_name(self):
        """Return full name of student/child."""
        return self._child_list_xml_root.find("Child").find("ChildName").text

    @property
    def full_name(self):
        return self.child_name

    @property
    def last_updated(self):
        """Return date of last API call for data refresh."""
        return self._last_updated

    @property
    def grade_book_xml(self):
        """Return raw xml of gradebook."""
        return self._grade_book_xml

    @property
    def child_list_xml(self):
        """Return raw xml of child list."""
        return self._child_list_xml

    @property
    def pxp_messages_xml(self):
        """Return raw xml of message listing."""
        return self._pxp_messages_xml

    @property
    def course_count(self):
        """Return total number of courses for student."""
        return self._course_count

    @property
    def gpa(self):
        """Return GPA calculation based on scores from non N/A courses."""
        if self._raw_grade_total:
            return round(
                self._raw_grade_total / (self._course_count - self._na_marks), 2
            )

    @property
    def missing_assignments(self):
        """Return total number of missing assignments from all courses."""
        return self._missing_assignments

    @property
    def reporting_period(self):
        """Return the reporting period such as Quarter 3."""
        return self._reporting_period.get("grade_period")

    @property
    def reporting_period_start(self):
        """Return the reporting period start date."""
        return self._reporting_period.get("start_date")

    @property
    def reporting_period_end(self):
        """Return the reporting period end date."""
        return self._reporting_period.get("end_date")

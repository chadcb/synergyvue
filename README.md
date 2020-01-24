# SynergyVUE Python Client

Access your StudentVUE information via Python.

## About

StudentVUE object provides access to student data via python WSDL.

StudentVUE is a product from [Edupoint](http://www.edupoint.com/Products/ParentVUE-StudentVUE) that schools use for both parents and students to access course and grade information. I'm not affiliated with or work for Edupoint.

This project is a result of wanting to provide student data as sensors/attributes for [Home Assistant](https://www.home-assistant.io/). If you are into home automation, definitely check out [Home Assistant](https://www.home-assistant.io/)!

## Installation

```bash
pip install synergyvue
```

## Usage

```python
from synergyvue import StudentVUE

student = StudentVUE('username', 'password', 'host')

student.id # Student ID from StudentVUE
student.name # First name from StudentVUE
student.full_name # Full name from StudentVUE
student.grade # Grade level of student. Ie, 07, 10, 12...
student.school # School Name
student.course_count # Total number of courses
student.gpa # Calculated from grade_raw total. Excludes courses where grade_letter is listed as N/A.
student.missing_assignments # Total number missing assignments for all courses
student.reporting_period # Ie, Quarter 3
student.reporting_period_start # Start date for this grading period
student.reporting_period_end # End date for this grading period
student.url # URL used for WSDL
student.last_updated # Date when data was fetched
student.meeting_date # For x/y alt day schedules
student.meeting_day  # for x/y alt day schedules

student.courses # Dictionary of courses. Course title is dict key.
  # title
  # id
  # room
  # staff
  # staff_email
  # mark_name
  # grade_letter
  # grade_raw
  # missing_assignments - Total missing assignments for this course
```

## StudentVUE vs ParentVUE?
StudentVUE is what an individual student uses to access their own information only. iOS apps and web interfaces are available for students to login.

ParentVUE is for parents to access their children's information. iOS app and web interface is available for parents to use.

The main difference is as a parent, you start up at a higher level and can pick which of your children you want to view information for. Once you choose a child, it then behaves pretty much the same as StudentVUE. Parents also have their own account to use so you don't have to worry about keeping track of your child account username/password.

## Testing
I am only able to test this with our public school district. However, doing google searches on SynergyVUE results in the URL's for the login page for other districts. By grabbing the hostname and adding the WSDL URL to the results, I am able to pull up the interface which looks the same as the one for our school. My assumption is this will work for anyone using StudentVUE. If you are able to test and verify, please let me know!

## TODO
- Add support for ParentVUE
- Ensure all error handling is correct

## Changelog & Releases
- 0.0.3 - Initial release considered alpha at this point

## License
MIT License
# Main code for interacting with course registration tasks

from enum import Enum
from bs4 import BeautifulSoup
import os
import sys
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time


# Object to encapsulate all things related to courses.
class Course:

    def __init__(self, id, dept, title='', section=1, prof=None, units=None):
        """
        params:
            id: course id/name. eg. "113"
            dept: department. e.g. "ACM"
            section: class section
        """
        self.id = id
        self.dept = dept
        self.title = title
        self.section = section
        self.prof = prof
        self.units = units

    def __str__(self):
        return f"""
        Course {self.dept} {self.id}
        Title: {self.title}
        Section: {self.section}
        Professor: {self.prof}"""

# Represents a request to either add or drop a course
class Request:

    RequestType = Enum('RequestType', 'Add Drop')

    def __init__(self, type, course):
        """
        params:
            type: Request type, should be RequestType enum
            course: Course object for the request
        """
        self.type = type
        self.course = course


# Common utility to login and initialize a webdriver
def initialize_driver(params):
    """
    Perform manual proxy login using selenium
    """
    url = "https://access.caltech.edu/regis_resp/owa2/citsss_webenr_students_pkg.main_course_enrollment?p_term_option_id=527"

    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
    driver.get(url)
    u = driver.find_element_by_name('login')
    u.send_keys(params['username'])
    p = driver.find_element_by_name('password')
    p.send_keys(params['password'])
    p.send_keys(Keys.RETURN)
    time.sleep(1)
    driver.switch_to_frame("mainFrame")

    return driver


# Main worker class that accesses information about currently enrolled courses
class Accessor:

    def __init__(self, params):
        """
        params:
            params: contains auth and other params
        """
        self.params = params
        self.driver = initialize_driver(params)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def _parse_course_table_row(self, first, second):
        """
        Given a pair of table rows describing the html trows content
        of a course, parse into a Course object.
        """
        dept, id = re.search("([A-Z]+)( *\d+)", first[0].text).groups()
        assert (dept is not None and id is not None)
        title = first[1].text
        section, prof = re.search("(\d+) (.*)", first[2].text).groups()

        course = Course(id, dept, title=title, section=section, prof=prof)
        return course

    def get_enrolled_courses(self):
        """
        Returns ids of all the enrolled courses
        """
        courses = []
        course_table = self.soup.find_all("table")[1].find_all("tr")[2:-2]
        for row_idx in range(0, len(course_table), 2):
            course = self._parse_course_table_row(course_table[row_idx].find_all("td"),
                                                  course_table[row_idx+1].find_all("td"))
            courses.append(course)

        return courses

    def check_enrolled(self, dept, id):
        """
        Returns boolean indicating whether given course is enrolled
        """
        enrolled_courses = self.get_enrolled_courses()
        for course in enrolled_courses:
            if course.dept == dept and course.id == id:
                return True

        return False

    def get_enrolled_course_info(self, dept, id):
        """
        Returns information about requested course
        """
        enrolled_courses = self.get_enrolled_courses()
        for course in enrolled_courses:
            if course.dept == dept and course.id == id:
                print(course)
        raise Exception("Invalid Course Input")


# Main worker class that performs registration requests
class Registor:

    def __init__(self, params):
        """
        params:
            params: contains auth and other params
        """
        self.params = params
        self.driver = initialize_driver(params)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def add_class(self, request):
        """
        For now just check whether we can enroll in the class
        params:
            request: Request object representing Add request
        """
        assert request.type == Request.RequestType.Add
        dept = request.course.dept
        id = request.course.id

        print(f"Adding Class {dept} {id}")

        self.driver.find_element_by_name('new_course_button').click()
        select = Select(self.driver.find_element_by_name('department_id_reqd'))
        select.select_by_visible_text(dept.upper())

        select = Select(self.driver.find_element_by_name('offering_id_reqd'))
        options = select.options
        offering_name = None
        for option in options:
            if re.search(id.upper(), option.text) is not None:
                offering_name = option.text
                break
        if offering_name is None:
            raise Exception("Invalid course ID")
        select.select_by_visible_text(offering_name)

    def drop_class(self, request):
        pass


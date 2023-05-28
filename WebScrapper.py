import re

import requests
import mysql.connector
from bs4 import BeautifulSoup


#  Compare Course from two given objects
def compareCourses(igecCoursesInString, nitCoursesInString):
    igecCourses = igecCoursesInString.strip("']['").split("', '")
    nitCourses = nitCoursesInString.strip("']['").split("', '")
    print("Common Course in IGEC & NIT")
    print(set(igecCourses) & set(nitCourses))


# Fetch course details from DB for given query
def fetchCourses(query):
    # Establish a connection to the MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="web_scrapper"
    )
    coursesInString = None
    # Create a cursor object to execute SQL queries
    cursor = db.cursor()
    cursor.execute(query)
    for listOfcourseInTuple in cursor:
        coursesInString = list(listOfcourseInTuple)[0]

    # Commit the changes and close the database connection
    db.commit()
    db.close()
    return coursesInString


# Store course details into DB
def storeCourse(collegeId, collageName, listOfCourse):
    # Establish a connection to the MySQL database
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="web_scrapper"
    )

    # Create a cursor object to execute SQL queries
    cursor = db.cursor()

    checkAvailablity = fetchCourses(
        "SELECT list_of_course FROM engineering_courses WHERE college_name = '" + collageName + "'")

    # Insert only if the record is not present
    if checkAvailablity is None:
        insert_query = "INSERT INTO engineering_courses (college_id, college_name, list_of_course) VALUES (%s,%s,%s)"
        values = (collegeId, collageName, listOfCourse)
        cursor.execute(insert_query, values)
    else:
        update_query = "UPDATE engineering_courses set college_name = %s, list_of_course = %s where college_id = %s"
        values = (collageName, listOfCourse, collegeId)
        cursor.execute(update_query, values)

    # Commit the changes and close the database connection
    db.commit()
    db.close()


# Fetch engineering courses from the IGEC website
url1 = 'https://www.igceng.com/dept/department'
response1 = requests.get(url1)
soup1 = BeautifulSoup(response1.text, 'html.parser')
engineering_courses_igec = []
courses_tags = []

def getCourse(listOftag):
    for tag in listOftag:
        coursename = tag[1].text
        engineering_courses_igec.append(coursename.replace('\xa0', ' '))


# Find the HTML elements containing the course information
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/h-s-8/h%26s'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/cse'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/dept-23/department'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/civil'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/eee'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/ece'))
courses_tags.append(soup1.find_all('a', href='https://www.igceng.com/it'))

course_elements_mech = soup1.find_all('a', href='https://www.igceng.com')
engineering_courses_igec.append(course_elements_mech[3].text)

getCourse(courses_tags)
storeCourse(3831, "Indra Ganesan College of Engineering", str(engineering_courses_igec))

# Fetch engineering courses from the NIT website
url2 = 'https://www.nitt.edu/home/admissions/btech/'
response2 = requests.get(url2)
soup2 = BeautifulSoup(response2.text, 'html.parser')
engineering_courses_nit = []

# Find the HTML elements containing the course information
course_elements_2 = soup2.find_all('a', {"href": re.compile('/home/academics/departments/.*')})

# Extract the course names and store them in a list
for course_element in course_elements_2:
    engineering_courses_nit.append(course_element.text)

# Remove non-engineerin course
engineering_courses_nit.pop()
storeCourse(3465, "National Institute of Technology", str(engineering_courses_nit))

# Fetch records from DB
igecCoursesInString = fetchCourses(
    "SELECT list_of_course FROM engineering_courses WHERE college_name = 'Indra Ganesan College of Engineering'")
nitCoursesInString = fetchCourses(
    "SELECT list_of_course FROM engineering_courses WHERE college_name = 'National Institute of Technology'")

# Compare course
compareCourses(igecCoursesInString, nitCoursesInString)

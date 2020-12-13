import argparse
import regis
import getpass
import re


def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--enroll', help='boolen for whether to enroll or drop', dest='enroll', action='store_true')
    args = arg_parser.parse_args()

    username = input("access.caltech username: ")
    password = getpass.getpass("access.caltech password: ")

    course_label = input("Enter course: ")
    dept, id = re.match("(\S+)(.*)", course_label).groups()
    id = id.lstrip()

    registor = regis.Registor({'username': username, 'password': password})

    course_obj = regis.Course(id, dept)
    if args.enroll is True:
        request = regis.Request(regis.Request.RequestType.Add, course_obj)
        registor.add_class(request)

    # registor.driver.close()
if __name__ == "__main__":
    main()

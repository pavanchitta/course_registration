import argparse
import regis
import getpass


def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--all', help='Get all course information', dest='all', required=False, default=False)
    arg_parser.add_argument('--course', help='[Course dept] [Course #]', dest='course', required =False, default='')
    args = arg_parser.parse_args()

    assert(args.all or args.course)

    username = input("access.caltech username: ")
    password = getpass.getpass("access.caltech password: ")

    accessor = regis.Accessor({'username':username, 'password': password})

    courses = accessor.get_enrolled_courses()
    if args.all:
        for course in courses:
            print(course)
    else:
        assert args.course
        dept, id = args.course.split(' ')
        accessor.get_enrolled_course_info(dept, id)


if __name__ == "__main__":
    main()
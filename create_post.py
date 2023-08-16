from getpass import getpass
import sys

from flask import current_app
from application import application
from flask_bcrypt import Bcrypt
from application import Poster,User, db, JobPost

def main():
    """Main entry point for script."""
    with application.app_context():
        db.metadata.create_all(db.engine)
        if Poster.query.all():
            print('A user already exists! Create another? (y/n):')
            create = input()
            if create == 'n':
                return

        print('Enter Username: ')
        username = input()
        print('Enter Unique Job ID (00001): ')
        jobid = input()
        while JobPost.query.get(jobid):
            print('That job ID already exists! Choose another please!')
            jobid = input()
        print('Enter Contact email: ')
        em = input()
        print('Enter Contact phone number: ')
        pn = input()
        print('Enter website URL: ')
        fn = input()
        print('Enter Company Description (2-3 words): ')
        ln = input()
        print('Enter Job Type (developer, graphic designer): ')
        ct = input()
        print('Enter Job Description (one sentence): ')
        st = input()
        print('Enter Pay Offered (hourly + equity): ')
        pt = input()
        print('Enter Job Duration (weeks, months, years): ')
        qt = input()
        print('Enter Start Date (11/25/21): ')
        rt = input()
        print('Enter skillset, notes, extra information: ')
        tt = input()

        jobpost = JobPost(
            username=username,
            jobid=jobid,
            contactemail=em,
            contactphone=pn,
            website=fn,
            companydescription=ln,
            jobtype=ct,
            jobdescription=st,
            payoffered=pt,
            jobduration=qt,
            startdate=rt,
            longdescription=tt,)
        db.session.add(jobpost)
        db.session.commit()
        print('Job Post added.')

bcrypt = Bcrypt()

if __name__ == '__main__':
    sys.exit(main())

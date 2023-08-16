from getpass import getpass
import sys

from flask import current_app
from application import application
from flask_bcrypt import Bcrypt
from application import Poster,User, db

def main():
    """Main entry point for script."""
    with application.app_context():
        db.metadata.create_all(db.engine)
        if Poster.query.all():
            print('A user already exists! Create another? (y/n):')
            create = input()
            if create == 'n':
                return

        print('Enter username: ')
        username = input()
        print('Enter email: ')
        em = input()
        print('Enter phone number: ')
        pn = input()
        print('Enter first name: ')
        fn = input()
        print('Enter last name: ')
        ln = input()
        print('Enter city: ')
        ct = input()
        print('Enter state: ')
        st = input()
        password = getpass()
        assert password == getpass('Password (again):')

        user = Poster(
            username=username,
            email=em,
            phonenumber=pn,
            firstname=fn,
            lastname=ln,
            city=ct,
            state=st,
            password=bcrypt.generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        print('User added.')

bcrypt = Bcrypt()

if __name__ == '__main__':
    sys.exit(main())
"""rackio/dao/auth.py

This module implements Authentication Data Objects Access.
"""
from .core import RackioDAO
import logging

from ..dbmodels import UserRole, User, Authentication
from ..utils import hash_password, verify_password, generate_key
from ..utils import verify_password as check_password


class AuthDAO(RackioDAO):

    def create(self, role, **kwargs):

        username = kwargs['username']
        if User.verify_username(username):

            return

        UserRole.select().where(UserRole.role==role).get()

        role = UserRole.select().where(UserRole.role==role).get()

        kwargs["password"] = hash_password(kwargs["password"])

        user = User.create(role_id=role.id, **kwargs)

        return user

    def read(self, username):

        try:

            user = User.select().where(User.username==username).get()

        except:

            return False

        return user

    def create_role(self, role):

        role = UserRole.create(role=role)

        return role

    def read_by_role(self, role):

        role = UserRole.select().where(UserRole.role==role).get()

        users = User.select().where(User.role_id==role.id)

        result = list()

        for user in users:

            result.append(user)
        
        return result

    def read_all(self):

        result = list()

        users = User.select()

        for user in users:

            result.append(user)

        return result

    def read_all_json(self):

        result = list()

        users = self.read_all()

        for user in users:

            user.role = self.get_role(user.name)
            result.append(user)

        return result

    def read_by_id(self, _id):

        user = User.select().where(User.id==_id).get()

        return user

    def read_by_key(self, key):

        try:
            auth = Authentication.select().where(Authentication.key==key).get()

            user = User.select().where(User.id==auth.user_id).get()

            return user
        
        except:

            return False

    def get_role(self, username):

        try:
            user = self.read(username)

            role = UserRole.select().where(UserRole.id==user.role_id).get()

            return role.role
            
        except:

            return False

    def update(self, username, role="", **kwargs):

        user = self.read(username)

        if "new_username" in kwargs:
            kwargs["username"] = kwargs["new_username"]
            del kwargs["new_username"]
        
        for key, value in kwargs.items():
            setattr(user, key, value)

        if role:
            role = UserRole.select().where(UserRole.role==role).get()

            user.role_id = role.id

        user.save()

        return True

    def delete(self, username):

        try:
            self.logout(username)
        except:
            pass

        user = User.select().where(User.username==username).get()

        user.delete_instance()
        
        return True

    def change_password(self, username, password):

        user = self.read(username)

        password = hash_password(password)

        user.password = password
        user.save()

    def verify_username(self, username):

        try:
            User.select().where(User.username==username).get()
        except:
            return False
        
        return True

    def login(self, username, password):

        user = self.read(username)

        if user:

            if verify_password(user.password, password):
                
                self._set_key(username)
                logging.info("{}: has logged in".format(username))

                return True

            return False

        return False

    def verify_password(self, username, password):

        user = self.read(username)

        if user:

            if check_password(user.password, password):

                return True

        return False

    def logout(self, username):

        self._delete_key(username)
        logging.info("{}: has logged out".format(username))
        return True
    
    def verify_key(self, key):

        try:
            Authentication.select().where(Authentication.key==key).get()
            return True
        except:
            return False

    def _delete_key(self, key):

        try:
            auth = Authentication.select().where(Authentication.key==key).get()
            auth.delete_instance()
        except:
            pass

    def _set_key(self, username):

        user = self.read(username)
        key = generate_key()
        
        self._delete_key(username)

        Authentication.create(user_id=user.id, key=key)

    def _get_key(self, username):

        user = self.read(username)

        try:
            auth = Authentication.select().where(Authentication.user_id==user.id).get()
        except:
            return False

        return auth.key

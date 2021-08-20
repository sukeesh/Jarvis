import json
import os
from getpass import getpass

from cryptography.fernet import Fernet

from packages.memory.memory import Memory

'''
This class allows storage of values in json format. It adds an easy
Interface to save values to disk.

The SAVE FUNCTION MUST BE RAN BEFORE THE OBJECT IS DESTROYED. This was by design
to limit the amount of time spent writing to disk.

This class creates a file called memory.json to store its data. If the
file doesnt exists it creates it and if it has already been created it loads
the data to memory.


example:
    m = Memory()
    name = m.get_data('firstName')
    m.add_data('lastName', 'albert')
    m.save()
'''
# this sets the path to the modules directory not the directory it was
# call from
module_path = os.path.dirname(__file__)


class KeyVault(Memory):
    """
        Initialize data with saved json file
    """

    def __init__(self, kv_file='key_vault.json'):
        super().__init__(kv_file)
        self._valid_api_key_names = []

    def add_valid_api_key_name(self, name):
        if name not in self._valid_api_key_names:
            self._valid_api_key_names.append(name)

    def get_valid_api_key_names(self):
        return sorted(self._valid_api_key_names)

    '''
        returns the json string
    '''

    def _generate_secret_key(self):
        self.enter_key_vault()
        secret_key = self.get_data("secret_key")
        if secret_key is None:
            secret_key = Fernet.generate_key()
            # TODO: fix this
            # password = self.first_key_vault_experience()
            # f = Fernet(password)
            # sha_secret_key = f.encrypt(secret_key)
            self.add_data("secret_key", secret_key.decode('utf-8'))
        self.exit_key_vault()
        return secret_key

    def first_key_vault_experience(self):
        print("This is the first time you are accessing the key vault!")
        print("Welcome!!")
        print("Let me start by giving you some information:")
        print("The key vault is to store your confidential information,")
        print("you know, things like passwords, or api secret and key combinations.")
        print("I also do want you to know that the key vault will keep everything encrypted for you.")
        print("Which means that I have algorithms built-in to hide information from others, for you.")
        print("But first, let us take a password from you to secure the key_vault.")
        print("We will not be storing this password!")
        print("At the same time, we will need this password to access any of your secrets,\n"
              "so please enter something you can remember later.")

        return getpass()

    def _get_secret_key(self):
        self.enter_key_vault()
        sha_secret_key = self.get_data("secret_key")
        # f = Fernet(getpass())
        # secret_key = f.decrypt(sha_secret_key.encode('utf-8')).decode('utf-8')
        self.exit_key_vault()
        return sha_secret_key

    def save_user_pass(self, key, user, password):
        """
            Saves user-pass to disk.
        """
        secret_key = self._generate_secret_key()
        f = Fernet(secret_key)
        sha_pass = f.encrypt(password.encode('utf-8'))

        user_pass = dict()
        user_pass['user'] = user
        user_pass['pass'] = sha_pass.decode('utf-8')
        self.data[key] = user_pass

    def get_user_pass(self, key):
        """
            Gets user-pass from disk.
        """
        secret_key = self._get_secret_key()

        try:
            user_pass = self.data[key]
        except BaseException:
            return None, None

        f = Fernet(secret_key)
        decrypt_pass = f.decrypt(user_pass['pass'].encode('utf-8')).decode('utf-8')
        return user_pass['user'], decrypt_pass

    def update_user_pass(self, key, user, password):
        """
            Updates user-pass on disk.
        """

        secret_key = self._get_secret_key()
        f = Fernet(secret_key)
        sha_pass = f.encrypt(password.encode('utf-8'))
        user_pass = dict()
        user_pass['user'] = user
        user_pass['pass'] = sha_pass.decode('utf-8')
        self.data[key] = user_pass

    def exit_key_vault(self):
        print("-" * 50 + "KEY-VAULT" + "-" * 50)

    def enter_key_vault(self):
        print("-" * 50 + "KEY-VAULT" + "-" * 50)

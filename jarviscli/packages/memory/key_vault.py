import json
import os
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

    '''
        returns the json string
    '''

    def generate_secret_key(self):
        secret_key = self.get_data("secret_key")
        if secret_key is None:
            secret_key = Fernet.generate_key()
            self.add_data("secret_key", secret_key.decode('utf-8'))
        return secret_key

    def get_secret_key(self):
        secret_key = self.get_data("secret_key")
        return secret_key

    def save_user_pass(self, key, user, password):
        """
            Saves user-pass to disk.
        """

        secret_key = self.generate_secret_key()
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

        secret_key = self.get_secret_key()

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

        secret_key = self.get_secret_key()
        f = Fernet(secret_key)
        sha_pass = f.encrypt(password.encode('utf-8'))
        user_pass = dict()
        user_pass['user'] = user
        user_pass['pass'] = sha_pass.decode('utf-8')
        self.data[key] = user_pass

import json
import os


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


class Memory:
    '''
        Initialize data with saved json file
    '''

    def __init__(self, mfile='memory.json'):
        self.json_file = os.path.join(module_path, mfile)
        self.data = ''
        # Try to open file if it doesnt exist it will throw an error
        try:
            with open(self.json_file, 'r') as f:
                self.data = json.load(f)
        except IOError:
            # create the new file with an empty json object
            with open(self.json_file, 'w') as f:
                f.write('{}')
            # add the data to the memory object
            with open(self.json_file, 'r') as f:
                self.data = json.load(f)

    '''
        returns the json string
    '''

    def get_all(self):
        return self.data

    '''
        get a specific key from memory
    '''

    def get_data(self, key):
        try:
            return self.data[key]
        except BaseException:
            return None

    '''
        add a key and value to memory
    '''

    def add_data(self, key, value):
        if self.get_data(key) is not None:
            print("data already exists with that name")
        else:
            self.data[key] = value

    '''
        Updates a key with supplied value.
    '''

    def update_data(self, key, value):
        self.data[key] = value

    '''
        delete a key from memory
    '''

    def del_data(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    '''
        !!!!DANGER!!!!!
        deletes the entire memory and overwrites the file with a blank file
        only use when absolutely needed.
    '''

    def del_all(self):
        with open(self.json_file, 'w') as f:
            f.write('')

    '''
        Saves memory to disk. This must be ran before memory object
        is destroyed. Otherwise all changes will be lost.
    '''

    def save(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.data, f)

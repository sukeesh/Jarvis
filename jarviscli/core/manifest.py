import os

import yaml

VALID_OS = ['linux', 'windows', 'macos', 'android', 'server']
OS_SHORTCUTS = {
    'desktop': ['linux', 'windows', 'macos'],
    'unix': ['linux', 'macos']
}

VALID_QUALITY = ['broken', 'legacy', 'default', 'tested']


class ManifestFile:
    def __init__(self, path):
        assert os.path.exists(path)
        self.path = os.path.basename(path)
        with open(path) as reader:
            self.data = yaml.load(reader.read(), Loader=yaml.SafeLoader)

    def __getitem__(self, val):
        return self.data[val]

    def verify(self):
        def is_str_list(l):
            assert isinstance(l, list), '{} is not a string list'.format(l)
            for val in l:
                assert isinstance(val, str), '{} is not a string'.format(val)

        if not 'alias' in self.data:
            self.data['alias'] = []

        # check keys are known
        for key, val in self.data.items():
            if key == 'name':
                if isinstance(val, list):
                    is_str_list(val[1:])
                    self.data['alias'].extend(val[1:])
                    val = val[0]
                    self.data[key] = val
                assert isinstance(val, str), \
                    "name {} is not a string".format(val)
            elif key == 'description':
                if isinstance(val, list):
                    val = [val]
                    self.data[key] = val
                is_str_list(val)
            elif key == 'requirements':
                if val is None:
                    continue
                assert isinstance(val, dict), \
                    'requirements {} is not a dict'.format(val)
                for r_key, r_val in val.items():
                    assert r_key in ['pip', 'native', 'apikey', 'os']
                    if isinstance(r_val, str):
                        r_val = [r_val]
                        val[r_key] = r_val
                    is_str_list(r_val)
            elif key == 'online':
                assert isinstance(val, bool), \
                    'online parameter {} is not a boolean'.format(val)
            elif key == 'quality':
                assert isinstance(val, str), \
                    'online quality {} is not a string'.format(val)
                assert val in VALID_QUALITY, \
                    "Quality {} not in {}".format(val, VALID_QUALITY)
            elif key == 'category':
                assert isinstance(val, str), \
                    "Category {} not a string".format(val)
            elif key == 'alias':
                is_str_list(val)
            else:
                assert False, 'Unknown key: {}'.format(key)

        # check required keys
        assert 'name' in self.data
        if not 'description' in self.data:
            self.data['description'] = ['']
        assert len(self.data['description']) > 0
        if not 'online' in self.data:
            self.data['online'] = True
        if not 'category' in self.data:
            self.data['category'] = []
        else:
            self.data['category'] = self.data['category'].split('/')
        if not 'quality' in self.data:
            self.data['quality'] = 'default'
        if not 'requirements' in self.data or not self.data['requirements']:
            self.data['requirements'] = {}
        req = self.data['requirements']

        if not 'pip' in req:
            req['pip'] = []
        if not 'native' in req:
            req['native'] = []
        if not 'apikey' in req:
            req['apikey'] = []
        if not 'os' in req:
            req['os'] = VALID_OS

        # verify os + os shortcuts
        os_no_duplicated = []
        for _os in req['os']:
            if _os in VALID_OS:
                if _os not in os_no_duplicated:
                    os_no_duplicated.append(_os)
                elif os in OS_SHORTCUTS:
                    for _os in OS_SHORTCUTS[_os]:
                        if _os not in os_no_duplicated:
                            os_no_duplicated.append(_os)
                else:
                    assert False, 'Unknown OS {}'.format(_os)
        req['os'] = os_no_duplicated

        return self


def load_manifests(folder_path: str):
    manifests = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.yaml') or file_name.endswith('.yml'):
            file_path = os.path.join(folder_path, file_name)
            try:
                manifest = ManifestFile(file_path)
                manifest.verify()
                manifests.append(manifest)
            except Exception as e:
                print('Failed to load: {}'.format(file_path))
                raise e

    return manifests

import os

import yaml

VALID_OS = ['linux', 'windows', 'macos', 'android', 'server']
OS_SHORTCUTS = {
    'desktop': ['linux', 'windows', 'macos'],
    'unix': ['linux', 'macos']
}

VALID_QUALITY = ['legacy', 'default', 'tested']


class ManifestFile:
    def __init__(self, path):
        assert os.path.exists(path)
        with open(path) as reader:
            self.data = yaml.load(reader.read(), Loader=yaml.SafeLoader)

    def __getitem__(self, val):
        return self.data[val]

    def verify(self):
        def is_str_list(l):
            assert isinstance(l, list)
            for val in l:
                assert isinstance(val, str), val

        # check keys are known
        for key, val in self.data.items():
            if key == 'name':
                assert isinstance(val, str)
            elif key == 'requirements':
                assert isinstance(val, dict)
                for r_key, r_val in val.items():
                    assert r_key in ['pip', 'native', 'apikey', 'os']
                    is_str_list(r_val)
            elif key == 'online':
                assert isinstance(val, bool)
            elif key == 'quality':
                assert isinstance(val, str)
                assert val in VALID_QUALITY
            else:
                assert False, 'Unknown key: {}'.format(key)

        # check required keys
        assert 'name' in self.data
        if not 'online' in self.data:
            self.data['online'] = True
        if not 'quality' in self.data:
            self.data['quality'] = 'default'
        if not 'requirements' in self.data:
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
            manifest = ManifestFile(file_path)
            manifest.verify()
            manifests.append(manifest)

    return manifests

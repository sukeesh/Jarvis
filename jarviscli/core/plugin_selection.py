import os

from dependency import Dependency
from manifest import load_manifests

PLUGIN_PATH = os.path.join(os.path.dirname(__file__), '..', 'plugins')


def run():
    manifests = load_manifests(PLUGIN_PATH)
    req_status = Dependency().check(manifests)
    print(req_status.print_count())
    print(req_status.print_disabled())


if __name__ == '__main__':
    run()

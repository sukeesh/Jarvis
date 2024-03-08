import os
import subprocess
import sys

from anytree import Node, PreOrderIter, RenderTree
from pickpack import PickPacker

from dependency import Dependency
from manifest import load_manifests

PLUGIN_PATH = os.path.join(os.path.dirname(__file__), '..', 'plugins')
PLUGIN_FILE = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))), 'plugins.txt')


def run():
    # receive plugins
    manifests = load_manifests(PLUGIN_PATH)
    req_status = Dependency().check(manifests)

    # print incompatible plugins
    print('Incompatible Plugins:')
    print(req_status.print_count())
    print(req_status.print_disabled())

    input("continue")

    # build node tree
    nodes = {}
    node_list = []
    for plugin in req_status.enabled:
        n = nodes
        for path in plugin['category']:
            if not path in n:
                n[path] = {}
            n = n[path]
            assert isinstance(n, dict)

        n[plugin['name']] = plugin

    # convert node tree (recursive)
    def build_node(name, node):
        children = []
        for key, value in sorted(node.items()):
            if isinstance(value, dict):
                children.append(build_node(key, value))
            else:
                if value['requirements']['pip']:
                    pip = ' (pip: ' + \
                        ', '.join(value['requirements']['pip']) + ')'
                else:
                    pip = ''
                node = Node(value['name'] + value['description'][0] + pip)
                node.data = value
                children.append(node)
                node_list.append(node)

        return Node(name, children=children)

    options = RenderTree(build_node('Plugins', nodes))

    # read old selection
    if os.path.exists(PLUGIN_FILE):
        with open(PLUGIN_FILE) as reader:
            plugins_enabled = reader.read().splitlines()
    else:
        plugins_enabled = []

    # run selection
    title = 'Please choose plugins (space and arrow keys): '
    picker = PickPacker(options,
                        title,
                        multiselect=True,
                        min_selection_count=1,
                        output_leaves_only=True,
                        output_format='nodeonly')
    picker.all_selected = [node.index for node in node_list
                           if node.data.path in plugins_enabled]
    selection = picker.start()

    # install requirements
    plugins_enabled = []
    failed_text = ""
    for plugin in selection:
        plugin = plugin.data
        pip = plugin['requirements']['pip']
        if len(pip) > 0:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install"] + pip)
            except:
                failed_text += "Installing packages {} for plugin {} failed; Disabling plugin \n".format(
                    pip, plugin['name'])
                continue
        plugins_enabled.append(plugin)

    print("\n\n")
    print(failed_text)

    with open(PLUGIN_FILE, 'w') as writer:
        for plugin in plugins_enabled:
            writer.write(plugin.path)
            writer.write('\n')

    print('Plugins enabled')


if __name__ == '__main__':
    run()

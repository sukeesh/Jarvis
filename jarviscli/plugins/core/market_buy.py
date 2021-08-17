# Modules
# Installing plugins
import os
from pathlib import Path

from plugin import Platform, plugin, require


@require(network=True, platform=[Platform.LINUX])
@plugin('market buy')
class market_buy():
    """
    Install baskets of plugins from Github Topics.

    Check the PLUGIN_MARKETPLACE.md for more information.
    """

    MARKETPLACE_PATH = 'marketplace'

    def parse_repo_link(self, repo):
        """We wish to extract the basket name from the whole repo link,
        and also throw errors if the repo is not okay.
        """
        repo_split = repo.split('/')
        # Eliminating the "github.com" part.
        repo_split = repo_split[3:]
        basket = repo_split[1]
        return basket

    def original_filepath(self, basket_filepath):
        """Find the original filepath from the basket filepath, that is,
        find the original parent folder.
        """
        target = Path(basket_filepath)
        target_parts = target.parts
        path_size = len(target_parts)
        # Excluding first path component.
        target = Path(target_parts[1])
        # We want all but the last comp., which is the file itself.
        for comp_index in range(2, path_size - 1):
            # Joining paths
            target = target / target_parts[comp_index]
        return target

    def add_new_lines(self, basket_file, original_file):
        """From the requirements.txt in the basket, inscribe new lines
        into the original requirements.txt.
        """
        with basket_file.open() as b_f:
            with original_file.open('a') as o_f:
                for line_bf in b_f:
                    print(f'Addition Line: {line_bf}')
                    o_f.write(line_bf)

    def __call__(self, jarvis, s):
        repo_link = 'https://github.com/' + s
        # basket = self.parse_repo_link(repo_link)

        # Git cloning into the plugin dir
        plugin_dir = os.path.join(self.MARKETPLACE_PATH, s)
        os.makedirs(plugin_dir, exist_ok=True)
        os.system('cd ' + plugin_dir + ' && git clone ' + repo_link + ' .')
        os.system('cd ' + plugin_dir + ' && ls -l')

        for root, dirs, files in os.walk(plugin_dir):
            if '.git' in root:
                continue
            else:
                for f in files:
                    if f == 'requirements.txt':
                        os.system('env/bin/pip install -U -r ' + os.path.join(root, f))

        jarvis.say('Operation completed. Please restart Jarvis.')

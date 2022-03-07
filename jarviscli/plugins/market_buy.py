import os
import shutil
import git
from plugin import Platform, plugin, require


@require(network=True)
@plugin('market buy')
class market_buy():
    """
    Install baskets of plugins from Github Topics.

    Check the PLUGIN_MARKETPLACE.md for more information.
    """
    # Absolute path for Jarvis/marketplace
    MARKETPLACE_PATH = os.path.join((os.sep).join(
        os.path.normpath(__file__).split(os.sep)[0:-3]),
        'marketplace')


    def __call__(self, jarvis, s):
        homepage = 'https://github.com/'
        if homepage in s:
            s = s.replace(homepage, '')
        repo_link = homepage + s

        # Git cloning into the plugin dir
        plugin_dir = os.path.join(self.MARKETPLACE_PATH, s)
        os.makedirs(plugin_dir, exist_ok=True)
        try:
            # In the case where the repo was already downloaded.
            shutil.rmtree(plugin_dir)
            os.makedirs(plugin_dir)
            target_dir = os.path.join(self.MARKETPLACE_PATH, s.split('/')[0])
            git.Git(target_dir).clone(repo_link)
        except ValueError as e:
            e('Please input a valid GitHub_User/Github_Repo.')
        os.system('cd ' + plugin_dir + ' && ls -l')

        for root, dirs, files in os.walk(plugin_dir):
            if '.git' in root:
                continue
            else:
                for f in files:
                    if f == 'requirements.txt':
                        jarvis_folder = os.path.split(self.MARKETPLACE_PATH)[0]
                        os.system((f'cd {jarvis_folder} && ' +
                                   'env/bin/pip install -U -r ' +
                                   os.path.join(root, f)))


        jarvis.say('Operation completed. Please restart Jarvis.')

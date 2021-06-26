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
    MAINTAIN_PYTHON_ONLY = True

    def cleanse_non_py(self, parent_folder):
        for root, dirs, files in os.walk(parent_folder):
            for f in files:
                if '.py' not in f:
                    os.unlink(os.path.join(root, f))

    def __call__(self, jarvis, s):
        homepage = 'https://github.com/'
        if homepage in s:
            s = s.replace(homepage, '')
        repo_link = homepage + s

        # Git cloning into the plugin dir
        plugin_dir = os.path.join(self.MARKETPLACE_PATH, s)
        os.makedirs(plugin_dir, exist_ok=True)
        try:
            target_dir = os.path.join(self.MARKETPLACE_PATH, s.split('/')[0])
            if os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
                os.makedirs(plugin_dir)
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

        # Deleting the .git folder from the cloned repo.
        shutil.rmtree(os.path.join(plugin_dir, '.git'))

        if self.MAINTAIN_PYTHON_ONLY:
            self.cleanse_non_py(plugin_dir)

        jarvis.say('Operation completed. Please restart Jarvis.')

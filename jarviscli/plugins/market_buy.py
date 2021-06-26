import os
from plugin import Platform, plugin, require


@require(network=True, platform=[Platform.LINUX])
@plugin('market buy')
class market_buy():
    """
    Install baskets of plugins from Github Topics. It accepts an
    Github_user/Github_repo that has the tag 'jarvis-plugin'.

    Check the PLUGIN_MARKETPLACE.md for more information.
    """

    MARKETPLACE_PATH = 'marketplace'

    def __call__(self, jarvis, s):
        homepage = 'https://github.com/'
        if homepage in s:
            s = s.replace(homepage, '')
        repo_link = homepage + s

        # Git cloning into the plugin dir
        plugin_dir = os.path.join(self.MARKETPLACE_PATH, s)
        os.makedirs(plugin_dir, exist_ok=True)
        try:
            os.system('cd ' + plugin_dir + ' && git clone ' + repo_link + ' .')
        except ValueError as e:
            e('Please input a valid GitHub_User/Github_Repo.')
        os.system('cd ' + plugin_dir + ' && ls -l')
        
        for root, dirs, files in os.walk(plugin_dir):
            if '.git' in root:
                continue
            else:
                for f in files:
                    if f == 'requirements.txt':
                        os.system('env/bin/pip install -U -r ' + os.path.join(root, f))
        
        # Deleting the .git folder from the cloned repo.
        os.rmdir(os.path.join(plugin_dir, '.git'))
        
        jarvis.say('Operation completed. Please restart Jarvis.')

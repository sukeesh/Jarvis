# Modules
# Installing plugins
import os
import tempfile
import shutil
import shutil
from pathlib import Path
# Jarvis
from colorama import Fore
from plugin import plugin, require, LINUX

@require(network=True, platform=[LINUX])
@plugin('market buy')
class market_buy():
    """
    Install baskets of plugins from Github Topics. 
    
    Check the PLUGIN_MARKETPLACE.md for more information.
    """
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
        #basket = self.parse_repo_link(repo_link)
        
        # Creating the temp directory
        temp_dir = tempfile.TemporaryDirectory(dir = os.getcwd())
        #print(f'HEY: {Path(temp_dir).name}')
        temp_name = temp_dir.name.replace(os.getcwd(), '')
        # The reason we need LINUX platform.
        temp_name = temp_name.replace('/', '')
        
        # Git cloning into the tempdir
        os.system('cd ' + temp_name + ' && git clone ' + repo_link + ' .')
        os.system('cd ' + temp_name + ' && ls -l')
            
        # Copying desired codes into the desired folders
        for root, dirs, files in os.walk(temp_name):
            if '.git' in root:
                continue
            else:
                for f in files:
                    if 'LICENSE' in files or 'README.md' in files:
                        continue
                    
                    elif root == temp_name:
                        basket_file = Path(root) / f
                        shutil.copyfile(basket_file, '')
                    
                    elif f == 'requirements.txt':
                        print(f'REQUIREMENTS?? {root + f}')
                        basket_file = Path(root) / f
                        original_file = self.original_filepath(basket_file)
                        self.add_new_lines(basket_file, original_file / f)
                        
                    else:
                        basket_file = Path(root) / f
                        original_folder = self.original_filepath(basket_file)
                        shutil.copyfile(basket_file, original_folder / f)
    
        # Cleaning everything in the tempdir
        temp_dir.cleanup()
        jarvis.say('Operation completed. Please reinstall Jarvis with "python installer ."')
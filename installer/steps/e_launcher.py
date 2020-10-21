from helper import *
from os.path import expanduser, exists
import unix_windows


# TODO Windows Install options?
if unix_windows.IS_WIN:
    fw = open('jarvis.bat', 'w')
    fw.write("""\
@ECHO off
CALL {JARVISPATH}\\env\\Scripts\\activate.bat
python {JARVISPATH}\\jarviscli\\
    """.format(JARVISPATH=os.getcwd()))
    section("FINISH")

    printlog("Installation Successful! Use 'jarvis' in cmd to start Jarvis!")
else:

    section("Write Jarvis starter")

    JARVIS_MACRO = """\
#!/bin/bash
source "{PATH}/env/bin/activate"
python "{PATH}/jarviscli" "$@"
    """

    fw = open('jarvis', 'w')
    fw.write(JARVIS_MACRO.format(PATH=os.getcwd()))
    fw.close()

    shell('chmod +x jarvis').should_not_fail()

    install_options = [("Install jarvis /usr/local/bin starter (requires root)", 0),
                       ("Add {} to $PATH (.bashrc)".format(os.getcwd()), 1),
                       ("Do nothing (Call Jarvis by full path)", 2)]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp jarvis /usr/local/bin')
    elif selection == 1:
        line_to_add = 'export PATH="$PATH:{}"'.format(os.getcwd())
        bashrc = '{}/.bashrc'.format(expanduser("~"))

        if not os.path.exists(bashrc):
            print("NO .bashrc found!")
        else:
            line_already_exists = False

            fr = open(bashrc)
            for line in fr.readlines():
                if line.startswith(line_to_add):
                    line_already_exists = True

            if line_already_exists:
                print("Jarvis path already added to $PATH in bashrc!")
            else:
                fw = open(bashrc, 'a')
                fw.write(line_to_add)
                fw.write('\n')
                fw.close()

    printlog('\n\nInstallation complete. Try using Jarvis!')
    if selection != 2:
        printlog('$ jarvis')
    else:
        printlog('$ {}/jarvis'.format(os.getcwd()))

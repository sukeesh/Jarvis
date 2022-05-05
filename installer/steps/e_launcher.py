from helper import *
from os.path import expanduser, exists
import unix_windows

# TODO Windows Install options?
if unix_windows.IS_WIN:
    fw = open('jarvis.bat', 'w')
    fw.write("""\
@ECHO off
CALL "{JARVISPATH}\\env\\Scripts\\activate.bat"
python "{JARVISPATH}\\jarviscli" %*
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
    # get the SHELL of the current user
    user_shell = get_default_shell()
    _do_nothing_str = "Do nothing (Call Jarvis by full path)"
    install_options = [("Install jarvis /usr/local/bin starter (requires root)", 0), ]
    if user_shell in SUPPORTED_SHELLS:
        install_options += [
            ("Add {} to $PATH (.{}rc)".format(os.getcwd(), user_shell, ), 1),
            (_do_nothing_str, 2)
        ]
    else:
        install_options += [
            (_do_nothing_str, 1)
        ]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp jarvis /usr/local/bin')
    elif selection == 1 and user_shell in SUPPORTED_SHELLS:
        line_to_add = 'export PATH="$PATH:{}"'.format(os.getcwd())
        shell_rc = '{}/.{}rc'.format(expanduser("~"), user_shell)

        if not os.path.exists(shell_rc):
            print("NO .{}rc found!".format(user_shell))
        else:
            line_already_exists = False

            fr = open(shell_rc)
            for line in fr.readlines():
                if line.startswith(line_to_add):
                    line_already_exists = True

            if line_already_exists:
                print("Jarvis path already added to $PATH in .{}rc!".format(user_shell))
            else:
                fw = open(shell_rc, 'a')
                fw.write(line_to_add)
                fw.write('\n')
                fw.close()

    printlog('\n\nInstallation complete. Try using Jarvis!')
    if selection == 0 or (selection == 1 and user_shell in SUPPORTED_SHELLS):
        printlog('$ jarvis')
    else:
        printlog('$ {}/jarvis'.format(os.getcwd()))

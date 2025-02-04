from helper import *
from os.path import expanduser, exists
import unix_windows

def supported_shell_install(rc_line_to_add : str, confirm_addition: bool) -> bool:
    shell_rc = '{}/.{}rc'.format(expanduser("~"), user_shell)
    if not os.path.exists(shell_rc):
        print("NO .{}rc found!".format(user_shell))
        return False;
    line_already_exists = False

    with open(shell_rc, "r") as fr:
        for line in fr.readlines():
            if line.startswith(rc_line_to_add):
                line_already_exists = True

    if line_already_exists:
        print("Jarvis path already added to $PATH in .{}rc!".format(user_shell))
        return True;

    print("")
    if not confirm_user_input("Allow Jarvis installation to add {} to .{}rc?".format(rc_line_to_add, user_shell)):
        print('Jarvis will not add "{}" to .{}rc.'.format(shell_rc, user_shell))
        print('In order to use Jarvis please manually add \'{}\' to your $PATH'.format(rc_line_to_add))
        return False
    with open(shell_rc, 'a') as fw:
        fw.write(line_to_add)
        fw.write('\n')
    return True

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
    home = os.getenv("HOME")
    xdg_install_path = "{}/.local/bin".format(home)
    if user_shell in SUPPORTED_SHELLS:
        install_options += [
            ("Add {} to $PATH (.{}rc)".format(os.getcwd(), user_shell, ), 1),
        ]
        if home != None and os.path.exists(xdg_install_path):
            install_options += [("Install jarvis to {}/.local/bin".format(home), 2)]
        install_options += [(_do_nothing_str, 3)]
    else:
        install_options += [
            (_do_nothing_str, 1)
        ]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp jarvis /usr/local/bin')
    elif user_shell in SUPPORTED_SHELLS:
        if selection == 1:
            line_to_add = 'export PATH="$PATH:{}"'.format(os.getcwd())
            supported_shell_install(line_to_add, True)
        elif selection == 2:
            os.system('cp jarvis {}'.format(xdg_install_path))
            line_to_add = 'export PATH="$PATH:{}"'.format(xdg_install_path)
            supported_shell_install(line_to_add, True)

    printlog('\n\nInstallation complete. Try using Jarvis!')
    if selection == 0 or (selection == 1 and user_shell in SUPPORTED_SHELLS):
        printlog('$ jarvis')
    else:
        printlog('$ {}/jarvis'.format(os.getcwd()))


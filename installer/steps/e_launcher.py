from helper import *
import unix_windows


# TODO Windows Install options?
if unix_windows.IS_WIN:
    fw = open('jarvis', 'w')
    fw.write("""\
@ECHO off
CALL {JARVISPATH}\\env\\Scripts\\activate.bat
python {JARVISPATH}\\jarviscli\\
    """.format(JARVISPATH=os.getcwd()))
    printlog("Installation Successful! Use 'jarvis' in cmd to start Jarvis!")
else:

    section("Write Jarvis starter")

    JARVIS_MACRO = """\
    #!/bin/bash
    source {PATH}/env/bin/activate
    python {PATH}/jarviscli
    """

    fw = open('jarvis', 'w')
    fw.write(JARVIS_MACRO.format(PATH=os.getcwd()))
    fw.close()

    install_options = [("Install jarvis /usr/local/bin starter (requires root)", 0),
                       ("Add {} to $PATH (.bashrc)".format(os.getcwd()), 1),
                       ("Do nothing (Call Jarvis by full path)", 2)]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp jarvis /usr/local/bin')
    elif selection == 1:
        os.system('export PATH=\\$PATH:{}" >> ~/.bashrc'.format(os.getcwd()))

    printlog('\n\nInstallation complete. Try unsing Jarvis!')
    if selection != 2:
        printlog('$ jarvis')
    else:
        printlog('$ {}/jarvis'.format(os.getcwd()))

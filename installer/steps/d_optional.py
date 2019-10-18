from helper import *
import optional
import unix_windows


section("Check optional requirements")

requirements_failed = []


def check_optional_requirement(requirement):
    if 'pip' in requirement.keys():
        packages = " ".join(requirement['pip'])
        CMD = "{} install -U {}".format(unix_windows.VIRTUALENV_PIP, packages)
        if shell(CMD).success():
            return True
        else:
            return False
    elif 'executable' in requirement.keys():
        requirement_ok = True
        for executable in requirement['executable']:
            if not executable_exists(executable):
                requirement_ok = False

        if requirement_ok:
            return True
        else:
            return False


for requirement in optional.OPTIONAL_REQUIREMENTS:
    if check_optional_requirement(requirement):
        printlog("* Success: {}".format(requirement['name']))
    else:
        printlog("* Fail: {}".format(requirement['name']))
        text = "{} - {}".format(requirement['name'], requirement['description'])
        requirements_failed.append((text, requirement))


section("Install *optional* non-python requirements")
requirements_failed.append(("Install nothing", 'exit'))

while True:
    requirement = user_input(requirements_failed)
    print('')
    print('')
    if requirement == 'exit':
        break

    guess = None

    printlog(requirement['name'])
    printlog('')
    printlog(requirement['instruction'])

    if 'package_guess' in requirement.keys():
        package = optional.get_guess(requirement['package_guess'])

        if package is not False:
            package_manager = optional.get_guess(optional.PackageManager)
            cmd = "{} {}".format(package_manager, package)

            print("\nOur Guess how to install:\n>{}".format(cmd))
    print('')
    input('continue  ')
    print('')
    print('')
    print('')

    if check_optional_requirement(requirement):
        printlog('Success!')
        requirements_failed = [x for x in requirements_failed if not x[0].startswith(requirement['name'])]
    else:
        printlog('Sorry; but looks like this did not work...')
    print('')

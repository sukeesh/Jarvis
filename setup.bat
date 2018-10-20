@echo off

:CheckError
if %errorlevel% neq 0 exit /b %errorlevel%
::check if virtualenv is installed

echo Admin permissions are required! Checking..
NET SESSION >nul 2>&1
if %errorLevel% == 2 (
  goto NoAdminRights
)

virtualenv --version || :goto VirtualEnvNotInstalled
echo "Virtualenv is installed!"

::Ask user for python version
SET /P pyversion=Specify Python Version(2/3)(Default: 3)
if "%pyversion%"=="" (
  SET pyversion=3
)
echo "You chose %pyversion%"

::save curred wd as jarvis path
FOR /F "tokens=*" %%g IN ('chdir') do (SET jarvispath=%%g)

echo "Jarvispath set as %jarvispath%"

::create jarvis run script
@echo @echo off >> jarvis.bat
@echo CALL %jarvispath%\env\Scripts\activate.bat >> jarvis.bat
@echo python %jarvispath%\jarviscli\ >> jarvis.bat

::create virtualenv

if "%pyversion%"=="2" (
  virtualenv env --python=python2
) ELSE (
  virtualenv env --python=python
)

::Disable Virtualenv prompt
SET VIRTUAL_ENV_DISABLE_PROMT=true

echo calling activate.bat
CALL %jarvispath%\env\Scripts\activate.bat
::install pip requirements
pip install --upgrade -r requirements.txt

::install ported windows packages
pip install PyPackages/curses_amd64.whl

echo Setting Path...
::make jarvis.bat executable form everywhere ; add it to path
SETX /M  PATH "%PATH%;%jarvispath%"

python -m nltk.downloader -d jarviscli/data/nltk wordnet

goto InstallationSucessful

:VirtualEnvNotInstalled
echo VirtualEnv needs to be installed!
PAUSE

:NoAdminRights
echo You need to run this script as an Admin!
PAUSE

:InstallationSucessful
echo WEE! Instalation Successful! Use 'jarvis' in cmd to start Jarvis!
PAUSE

@echo off

::Check if Virtualenv is installed!
virtualenv --version || :goto VirtualEnvNotInstalled
echo "Virtualenv is installed!"


::save curred wd as jarvis path
FOR /F "tokens=*" %%g IN ('chdir') do (SET jarvispath=%%g)

echo "Jarvispath set as %jarvispath%"

::create jarvis run script
break>jarvis.bat
@echo @echo off >> jarvis.bat
@echo CALL %jarvispath%\env\Scripts\activate.bat >> jarvis.bat
@echo python %jarvispath%\jarviscli\ >> jarvis.bat

::create virtualenv
virtualenv env --python=python

::Disable Virtualenv prompt
SET VIRTUAL_ENV_DISABLE_PROMT=true

echo calling activate.bat
CALL %jarvispath%\env\Scripts\activate.bat
::install pip requirements
pip install --upgrade -r requirements.txt

::install windows specifix requirements
pip install --upgrade -r requirements_windows.txt

echo Setting Path...
::save user path first
FOR /F "tokens=3 skip=2" %%G IN ('reg query HKCU\Environment /v Path') DO (SET userpath=%%G)
::add jarvispath to user path
setx path %userpath%;%jarvispath%

python -m nltk.downloader -d jarviscli/data/nltk wordnet

goto InstallationSucessful

:VirtualEnvNotInstalled
echo VirtualEnv needs to be installed!
PAUSE

:InstallationSucessful
echo WEE! Instalation Successful! Use 'jarvis' in cmd to start Jarvis!
PAUSE

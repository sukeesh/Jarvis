@echo off

::Check if Virtualenv is installed!
virtualenv --version || :goto VirtualEnvNotInstalled
echo "Virtualenv is installed!"


::save curred wd as jarvis path
FOR /F "tokens=*" %%g IN ('chdir') do (SET jarvispath=%%g)

echo "Jarvispath set as %jarvispath%"

::create jarvis run script
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

echo Setting Path...
::make jarvis.bat executable form everywhere ; add it to path
SETX PATH "%PATH%;%jarvispath%"

python -m nltk.downloader -d jarviscli/data/nltk wordnet

goto InstallationSucessful

:VirtualEnvNotInstalled
echo VirtualEnv needs to be installed!
PAUSE

:InstallationSucessful
echo WEE! Instalation Successful! Use 'jarvis' in cmd to start Jarvis!
PAUSE

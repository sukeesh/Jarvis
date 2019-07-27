@ECHO off

::Check if virtualenv is installed!
virtualenv --version
IF %ERRORLEVEL% NEQ 0 GOTO VirtualEnvNotInstalled
ECHO "Virtualenv is installed!"

::save curred directory as jarvis path
FOR /F "tokens=*" %%g IN ('chdir') DO (SET jarvispath=%%g)

ECHO "Jarvispath set as %jarvispath%"

::create jarvis run script
COPY NUL jarvis.bat
@ECHO @ECHO off >> jarvis.bat
@ECHO CALL %jarvispath%\env\Scripts\activate.bat >> jarvis.bat
@ECHO python %jarvispath%\jarviscli\ >> jarvis.bat

::create virtualenv
virtualenv env --python=python

::disable virtualenv prompt
SET VIRTUAL_ENV_DISABLE_PROMT=true

ECHO calling activate.bat
CALL %jarvispath%\env\Scripts\activate.bat
::install pip requirements
pip install --upgrade -r requirements.txt

ECHO Setting Path...
::save user path first
FOR /F "tokens=3 skip=2" %%G IN ('reg query HKCU\Environment /v Path') DO (SET userpath=%%G)
::add jarvispath to user path
setx path %userpath%;%jarvispath%

python -m nltk.downloader -d jarviscli/data/nltk wordnet

GOTO InstallationSuccessful

:VirtualEnvNotInstalled
ECHO VirtualEnv needs to be installed!
EXIT

:InstallationSuccessful
ECHO Installation Successful! Use 'jarvis' in cmd to start Jarvis!
PAUSE

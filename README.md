# Jarvis
Personal Assistant for Linux

![Jarvis](http://i.imgur.com/xZ8x9ES.jpg)

> **What is this?**

- A simple personal assistant for Linux which works on terminal.

> **How to use?**

- Just clone the repository and run `python Jarvis`
- Please check `requirements.txt` to install dependencies.
- Tip: use the command `pip install -r requirements.txt` to install the requirements

> **Youtube Video**

[Click here](https://www.youtube.com/watch?v=PR-nxqmG3V8)

> **Contributors**

- PR's are accepted!!

- HOW TO EXTEND JARVIS:
 If you would like to add extra functionality to Jarvis (for example new actions like "record" etc.) you only need to add this action to the action dict (look on __init__(self) in Jarvis.py) along with a apropriate function name. Then you need to implement this function as a local function on reactions() method.

 ### How to run tests:
 Change into the Jarvis/Jarvis directory
 ```bash
 cd Jarvis/Jarvis
 ```
 Then run unittest discover
 ```python
 python -m unittest discover
 ```

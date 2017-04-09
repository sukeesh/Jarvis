# Jarvis
A Personal Assistant for Linux

![Jarvis](http://i.imgur.com/xZ8x9ES.jpg)

Jarvis is a simple personal assistant for Linux which works on terminal. He can talk to you if you enable his voice. He can tell you the weather, he can find restaurants and and other places near you. He can do some great stuff for you.

## Getting Started

In order to start Jarvis just clone the repository and run the command: `python Jarvis`.

### Prerequisites

Use the command `pip install -r requirements.txt` to install the requirements.

## Youtube Video

[Click here](https://www.youtube.com/watch?v=PR-nxqmG3V8)

## Contributing

- PR's are accepted!!
- If you have some ideas for new features and you don't have time to implement them please open an issue with the tag new_feature
- If you have time to add extra functionality to Jarvis (for example new actions like "record" etc.) you only need to add this action to the action dict (look on init(self) in Jarvis.py) along with a apropriate function name. Then you need to implement this function as a local function on reactions() method.
- Please don't forget to comment (document) your code

 ### How to run tests:
 Change into the Jarvis/Jarvis directory
 ```bash
 cd Jarvis/Jarvis
 ```
 Then run unittest discover
 ```python
 python -m unittest discover
 ```

## Authors

 **sukeesh** 

See also the list of [contributors](contributors.md) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

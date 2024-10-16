Overview
The SoccerScores plugin is designed to fetch and display the latest soccer scores from major games using TheSportsDB API. This plugin is integrated into the Jarvis command-line interface, allowing users to get real-time soccer game updates directly from their terminal.

Requirements
Python 3.x
The requests library installed (pip install requests)
The Jarvis command-line interface setup
An active internet connection (as this plugin requires network access)
Installation
This plugin should be placed in the Jarvis plugins directory. No additional installation steps are needed beyond ensuring that all dependencies (like the requests library) are installed. Here is how you can place it:

Navigate to the Jarvis plugins directory (typically found at jarviscli/plugins).
Add the SoccerScores.py file to this directory.
Usage
To use the SoccerScores plugin within Jarvis, invoke the plugin through the command line:

soccer
This command is set up via the @alias("soccer") decorator, making it easy to remember and use.

Class and Methods
SoccerScores

Purpose: Fetches and displays live soccer scores from TheSportsDB API.
Methods:
__call__(self, jarvis, s): This method is the entry point for the Jarvis plugin activation. It calls the print_latest_scores method.
print_latest_scores(self, jarvis): Handles the communication with TheSportsDB API, processes the JSON data, and outputs the soccer scores to the user.
Detailed Method Description
print_latest_scores(self, jarvis)

Parameters:
jarvis: Instance of JarvisAPI, used to interact with the user.
Functionality:
Makes an HTTP GET request to TheSportsDB API to fetch the latest soccer scores.
Parses the JSON response and formats the output to display match details such as event, date, score, and status.
Handles potential network errors gracefully and informs the user if any issues occur or if no data is found.
Example
To check the latest soccer scores, simply type the following command in the Jarvis interface:

soccer
Follow the interactive prompts if any, and view the latest scores as they are fetched and displayed.

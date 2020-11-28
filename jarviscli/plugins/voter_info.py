"""Jarvis plugin to get public voter information based on the users address."""
import json
import geopy
import urllib.parse
import requests
import shutil
import os
from packages.mapps import get_location
from colorama import Fore

# All plugins should inherite from this library
from plugin import plugin

DATA_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = DATA_PATH[:-8] + "/data"
KEY_JSON_FILE = "/Google_api_key.json"
KEY = ""


def print_address(jarvis, location, address):
    """Output polling location information."""
    site_info = ""
    for line in address:
        if line == "state":
            break
        if address[line]:
            site_info += str(address[line]) + ", "
    site_info += address["state"] + " " + address["zip"]
    jarvis.say(site_info, Fore.RED)
    jarvis.say("Hours:", Fore.RED)
    jarvis.say(location["pollingHours"], Fore.RED)
    dateRange = "From " + location["startDate"] + " to " + location["endDate"]
    jarvis.say(dateRange, Fore.RED)
    jarvis.say("----------------------------------------")


def get_voter_info(jarvis, s, address):
    """Get voter info from API and output to user."""
    # Formulate API request
    url = "https://www.googleapis.com/civicinfo/v2/voterinfo?key="
    url += KEY
    url += "&address=" + urllib.parse.quote(str(address))
    if s:
        url += "&electionId=" + s
    result = requests.get(url)
    voterInfo = result.json()

    # Return information to user
    if "election" not in voterInfo:
        # exit if no info found
        jarvis.say(
            "Sorry, I wasn't able to find any election information for your location.",
            Fore.RED,
        )
        return -1
    election_title_str = (
        "Showing results for "
        + str(voterInfo["election"]["name"])
        + " on "
        + str(voterInfo["election"]["electionDay"])
    )
    jarvis.say(election_title_str, Fore.RED)

    # Print polling locations
    if "pollingLocations" in voterInfo:
        jarvis.say("----------------------------------------")
        jarvis.say("You can vote at these addresses:", Fore.BLUE)
        for location in voterInfo["pollingLocations"]:
            print_address(jarvis, location, location["address"])

    # Print early polling locations
    if "earlyVoteSites" in voterInfo:
        jarvis.say("----------------------------------------")
        jarvis.say("You can vote early at these adddresses", Fore.BLUE)
        for location in voterInfo["earlyVoteSites"]:
            print_address(jarvis, location, location["address"])

    # Print drop off locations
    if "dropOffLocation" in voterInfo:
        jarvis.say("----------------------------------------")
        jarvis.say("There are absentee ballot drop boxes at these addresses", Fore.BLUE)
        for location in voterInfo["dropOffLocation"]:
            print_address(jarvis, location, location["address"])

    if "otherElections" in voterInfo:
        jarvis.say("----------------------------------------")
        jarvis.say("There are also these elections in your area:", Fore.BLUE)
        for election in voterInfo["otherElections"]:
            election_title_str = (
                str(election["name"])
                + " on "
                + str(election["electionDay"])
                + " id: "
                + str(election["id"])
            )
            jarvis.say(election_title_str, Fore.RED)
        jarvis.say(
            "To get more information on these elections just say 'voterinfo' followed by the election id",
            Fore.BLUE,
        )

    return voterInfo


@plugin("voterinfo")
def voter_info(jarvis, s):
    """
    Jarvis plugin that gets public voter information based on user's address.

    Usage:
    voterinfo electionID

    Returns:
    Prints Polling locations available to the user and any
    other elections as well as their ID that they can look
    up besides the one provided. Additionally stores much more
    information in VoterInfo.json in the user's current directory.

    """
    # Welome message
    jarvis.say("Welcome to the Jarvis Voter Information plugin!", Fore.BLUE)

    # Get user API key
    if not os.path.isfile(DATA_PATH + KEY_JSON_FILE):
        shutil.copy2(
            DATA_PATH + "/sampleGoogle_api_key.json", DATA_PATH + KEY_JSON_FILE
        )

    with open(DATA_PATH + KEY_JSON_FILE) as json_file:
        json_obj = json.load(json_file)
        global KEY
        KEY = str(json_obj["key"])
        if KEY == "YOUR_KEY_HERE":
            jarvis.say(
                "In order to use the Voter Information Plugin you will need a Google API key.\n"
                + "Please create an API key here: https://console.developers.google.com/apis/credentials\n"
                + "then copy the value to 'key' in jarviscli/data/Google_api_key.json\n"
                + "To create an api key you must select a project (creating one if you do not have one yet)"
                + ", then you must select 'create credentials' > 'API key'.\n"
                + "More detailed instructions can be found here: "
                + "https://developers.google.com/civic-information/docs/using_api\n",
                Fore.BLUE,
            )
            return

    jarvis.say("Please wait while I get your location ....", Fore.BLUE)

    # Get users location
    current_location = get_location()
    coordinates = (
        str(current_location["latitude"]) + ", " + str(current_location["longitude"])
    )
    geo = geopy.geocoders.Nominatim(user_agent="Jarvis")
    address = geo.reverse(coordinates)

    # Verify location with user
    user_check_location = "I have your location as " + str(address)
    jarvis.say(user_check_location, Fore.RED)
    user_confirmation = jarvis.input("Is this correct? (yes/no)\n")
    if user_confirmation == "no":
        address = jarvis.input("Please enter your correct address .... \n")

    # Get election info
    elections = get_voter_info(jarvis, s, address)

    # Store all information to local directory
    if elections != -1:
        jarvis.say(
            "More info has been stored in 'VoterInfo.json' in your current directory.",
            Fore.BLUE,
        )
        with open("VoterInfo.json", "w+") as outfile:
            json.dump(elections, outfile, indent=2)

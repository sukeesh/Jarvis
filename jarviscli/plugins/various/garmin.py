#!/usr/bin/env python3
from plugins.user_pass import user_pass
from plugin import require, plugin


GARMIN = "garminconnect"


@require(network=True)
@plugin("garmin connect")
def connect_garmin(jarvis, s):
    """
    Initialize Garmin client with credentials
    Only needed when your program is initialized
    """
    from garminconnect import Garmin
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )

    jarvis.garmin_client = None
    jarvis.say("Attempting connect...")

    user, pass_word = jarvis.internal_execute("user pass", GARMIN)

    try:
        jarvis.garmin_client = Garmin(user, pass_word)
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client init: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client init")
        return

    """
    Login to Garmin Connect portal
    Only needed at start of your program
    The library will try to relogin when session expires
    """
    jarvis.say("Logging in Garmin client...")
    try:
        jarvis.garmin_client.login()
        jarvis.say("Client Logged in")
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client login: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client login")
        return


def call_connect(jarvis, s):
    if hasattr(jarvis, "garmin_client"):
        return
    jarvis.internal_execute('garmin connect', "")


def call_stats(jarvis, s):
    if hasattr(jarvis, 'garmin_stats'):
        return
    jarvis.execute_once('garmin stats')


def group_stats(incoming_stats):
    stats = dict()
    heart_rate = dict()
    sleep = dict()
    stress = dict()
    activity = dict()
    wellness = dict()
    floors = dict()
    body_battery = dict()
    intensity = dict()
    calories = dict()
    steps = dict()
    spo2 = dict()

    for (key, value) in incoming_stats.items():
        # CALORIES
        if "calorie" in key or "Calorie" in key:
            calories[key] = value
        # STEPS
        elif "step" in key or "Step" in key:
            steps[key] = value
        # HEART RATE
        elif "Heart" in key or "heart" in key:
            heart_rate[key] = value
        # SPO2
        elif "Spo2" in key or "spo2" in key:
            spo2[key] = value
        # STRESS
        elif "Stress" in key or "stress" in key:
            stress[key] = value
        # SLEEP
        elif "sleep" in key or "Sleep" in key or "sedentary" in key or "sedentary" in key:
            sleep[key] = value
        elif "awake" in key or "Awake" in key:
            sleep[key] = value
        # ACTIVITIES
        elif "wellness" in key or "Wellness" in key:
            wellness[key] = value
        elif "floors" in key or "Floors" in key:
            floors[key] = value
        elif "bodyBattery" in key:
            body_battery[key] = value
        elif "intensity" in key or "Intensity" in key:
            intensity[key] = value
        # GENERAL IN ACTIVITIES
        elif "active" in key or "Active" in key or "activity" in key or "Activity" in key:
            activity[key] = value
        elif 'total' in key or "duration" in key:
            activity[key] = value
        else:
            stats[key] = value

    stats['heart_rate'] = heart_rate
    stats['calories'] = calories
    stats['steps'] = steps
    stats['spo2'] = spo2
    stats['stress'] = stress
    stats['sleep'] = sleep
    activity['wellness'] = wellness
    activity['floors'] = floors
    activity['body_battery'] = body_battery
    activity['intensity'] = intensity
    stats['activity'] = activity

    return stats


@require(network=True)
@plugin("garmin client name")
def garmin_client_name(jarvis, s):
    """
    Get full name from profile
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )

    call_connect(jarvis, s)

    try:
        jarvis.say("Garmin Client Full name: " + jarvis.garmin_client.get_full_name())
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get full name: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get full name")
        return


@require(network=True)
@plugin("garmin stats")
def garmin_stats(jarvis, s):
    """
        Get unit system from profile
        """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Printing garmin stats for today!")
    try:
        stats = jarvis.garmin_client.get_stats(date.today().isoformat())
        jarvis.garmin_stats = group_stats(stats)
        jarvis.say(json.dumps(jarvis.garmin_stats, indent=2))

    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get stats: %s" % err)
        return
    except Exception as exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get stats: %s" % exception)
        return


@require(network=True)
@plugin("garmin unit system")
def garmin_unit_system(jarvis, s):
    """
    Get unit system from profile
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    call_connect(jarvis, s)

    try:
        jarvis.say("Garmin unit System: " + jarvis.garmin_client.get_unit_system())
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get unit system: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get unit system")
        return


@require(network=True)
@plugin("garmin activity")
def garmin_activity_today(jarvis, s):
    """
    Get activity data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Printing Activity information for {" + str(date.today().isoformat()) + "}")
    try:
        jarvis.say(json.dumps(jarvis.garmin_client.get_activities(0, 10), indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get stats: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get stats")
        return


@require(network=True)
@plugin("garmin steps")
def garmin_steps(jarvis, s):
    """
    Get steps data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Getting steps information for date: {" + str(date.today().isoformat()) + "}")
    try:
        jarvis.say(json.dumps(jarvis.garmin_client.get_steps_data(date.today().isoformat()), indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get steps data: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get steps data")
        return


@require(network=True)
@plugin("garmin heart rate")
def garmin_heart_rate(jarvis, s):
    """
    Get heart rate data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Getting heart rate information for date: {" + str(date.today().isoformat()) + "}")
    try:
        jarvis.say(json.dumps(
            jarvis.garmin_client.get_heart_rates(date.today().isoformat()),
            indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get heart rates: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get heart rates")
        return


@require(network=True)
@plugin("garmin body composition")
def garmin_body_composition(jarvis, s):
    """
    Get body composition data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Getting Body Composition information for date: {" + str(date.today().isoformat()) + "}")
    try:
        jarvis.say(json.dumps(
            jarvis.garmin_client.get_body_composition(date.today().isoformat()),
            indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get body composition: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get body composition")
        return


@require(network=True)
@plugin("garmin stats and body")
def garmin_stats_and_body(jarvis, s):
    """
    Get stats and body composition data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Getting Stats and Body Composition information for date: {" + str(date.today().isoformat()) + "}")

    try:
        jarvis.say(json.dumps(jarvis.garmin_client.get_stats_and_body(date.today().isoformat()), indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get stats and body composition: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get stats and body composition")
        return


@require(network=True)
@plugin("garmin sleep")
def garmin_sleep(jarvis, s):
    """
    Get sleep data
    """
    from garminconnect import (
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    from datetime import date
    import json

    call_connect(jarvis, s)

    jarvis.say("Getting Sleep information for date: {" + str(date.today().isoformat()) + "}")
    try:
        jarvis.say(json.dumps(jarvis.garmin_client.get_sleep_data(date.today().isoformat()), indent=2))
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        jarvis.say("Error occurred during Garmin Connect Client get sleep data: %s" % err)
        return
    except Exception:  # pylint: disable=broad-except
        jarvis.say("Unknown error occurred during Garmin Connect Client get sleep data")
        return
#
# """
# Download an Activity
# """
# try:
#     for activity in activities:
#         activity_id = activity["activityId"]
#         jarvis.say("garmin_client.download_activities(%s)", activity_id)
#         jarvis.say("----------------------------------------------------------------------------------------")
#
#         gpx_data = garmin_client.download_activity(activity_id, dl_fmt=garmin_client.ActivityDownloadFormat.GPX)
#         output_file = f"./{str(activity_id)}.gpx"
#         with open(output_file, "wb") as fb:
#             fb.write(gpx_data)
#
#         tcx_data = garmin_client.download_activity(activity_id, dl_fmt=garmin_client.ActivityDownloadFormat.TCX)
#         output_file = f"./{str(activity_id)}.tcx"
#         with open(output_file, "wb") as fb:
#             fb.write(tcx_data)
#
#         zip_data = garmin_client.download_activity(activity_id, dl_fmt=garmin_client.ActivityDownloadFormat.ORIGINAL)
#         output_file = f"./{str(activity_id)}.zip"
#         with open(output_file, "wb") as fb:
#             fb.write(zip_data)
#
#         csv_data = garmin_client.download_activity(activity_id, dl_fmt=garmin_client.ActivityDownloadFormat.CSV)
#         output_file = f"./{str(activity_id)}.csv"
#         with open(output_file, "wb") as fb:
#           fb.write(csv_data)
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get activity data: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get activity data")
#     return
#
#

#
#
# """
# Get devices
# """
# jarvis.say("garmin_client.get_devices()")
# jarvis.say("----------------------------------------------------------------------------------------")
# try:
#     devices = garmin_client.get_devices()
#     jarvis.say(devices)
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get devices: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get devices")
#     return
#
#
# """
# Get device settings
# """
# try:
#     for device in devices:
#         device_id = device["deviceId"]
#         jarvis.say("garmin_client.get_device_settings(%s)", device_id)
#         jarvis.say("----------------------------------------------------------------------------------------")
#
#         jarvis.say(garmin_client.get_device_settings(device_id))
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get device settings: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get device settings")
#     return

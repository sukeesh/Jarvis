#!/usr/bin/env python3

from plugin import require, plugin


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

    user = jarvis.input("UserID: ")  # YOUR ID
    pass_word = jarvis.input("\nPassword: ", password=True)  # YOUR Password

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
    jarvis.execute_once('garmin connect')


def call_stats(jarvis, s):
    if hasattr(jarvis, 'garmin_stats'):
        return
    jarvis.execute_once('garmin stats')


def group_stats(stats):
    heart_rate = dict()
    sleep = dict()
    stress = dict()
    activity = dict()
    calories = dict()
    steps = dict()
    spo2 = dict()

    for (key, value) in stats.items():
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
        # REST
        else:
            activity[key] = value

    stats = dict()
    stats['heart_rate'] = heart_rate
    stats['calories'] = calories
    stats['steps'] = steps
    stats['spo2'] = spo2
    stats['stress'] = stress
    stats['activity'] = activity

    return stats


def ignore_none(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(d.items()):
        if (value is None) or (value == "null"):
            del d[key]
        elif isinstance(value, dict):
            ignore_none(value)
    return d  # For convenience


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
    from datetime import date, datetime
    import json

    call_connect(jarvis, s)

    jarvis.say("Printing garmin stats for today!")
    try:

        stats = jarvis.garmin_client.get_stats(date.today().isoformat())
        jarvis.garmin_stats = group_stats(stats)
        jarvis.garmin_stats['timestamp'] = datetime.now()
        jarvis.say(json.dumps(
            jarvis.garmin_stats,
            indent=2))
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
        jarvis.say(json.dumps(jarvis.garmin_client.get_stats(date.today().isoformat()), indent=2))
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

#
# """
# Get stats and body composition data
# """
# jarvis.say("garmin_client.get_stats_and_body_composition(%s)", today.isoformat())
# jarvis.say("----------------------------------------------------------------------------------------")
# try:
#     jarvis.say(garmin_client.get_stats_and_body(today.isoformat()))
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get stats and body composition: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get stats and body composition")
#     return
#
#
# """
# Get activities data
# """
# jarvis.say("garmin_client.get_activities(0,1)")
# jarvis.say("----------------------------------------------------------------------------------------")
# try:
#     activities = garmin_client.get_activities(0,1) # 0=start, 1=limit
#     jarvis.say(activities)
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get activities: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get activities")
#     return
#
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
# """
# Get sleep data
# """
# jarvis.say("garmin_client.get_sleep_data(%s)", today.isoformat())
# jarvis.say("----------------------------------------------------------------------------------------")
# try:
#     jarvis.say(garmin_client.get_sleep_data(today.isoformat()))
# except (
#     GarminConnectConnectionError,
#     GarminConnectAuthenticationError,
#     GarminConnectTooManyRequestsError,
# ) as err:
#     jarvis.say("Error occurred during Garmin Connect Client get sleep data: %s" % err)
#     return
# except Exception:  # pylint: disable=broad-except
#     jarvis.say("Unknown error occurred during Garmin Connect Client get sleep data")
#     return
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

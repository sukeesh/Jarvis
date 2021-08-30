from plugin import Platform, plugin, require


@plugin("status")
def status(jarvis, s):
    jarvis.say(jarvis.dependency_status.print_count())

    if "short" not in s:
        jarvis.say(jarvis.dependency_status.print_disabled())

    jarvis.say("")
    count_enabled = len(jarvis.active_frontends)
    count_total = len(jarvis.AVAILABLE_FRONTENDS)
    jarvis.say(
        "{} out of {} Frontends enabled".format(
            count_enabled,
            count_total))
    for frontend in jarvis.active_frontends:
        jarvis.say("{:<20}: {}".format(frontend, "ACTIVE"))
    jarvis.say(jarvis.frontend_status.print_disabled())

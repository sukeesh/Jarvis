from plugin import Platform, plugin, require, quality, QualityLevel


@quality(QualityLevel.CORE)
@plugin("status")
def status(jarvis, s):
    jarvis.say(jarvis.dependency_status.print_count())

    if "short" not in s:
        jarvis.say(jarvis.dependency_status.print_disabled())

    active_disabled = jarvis.dependency_status.active_disabled
    if len(active_disabled) > 0:
        jarvis.say("{} plugins disabled or do not match quality status:\n{}".format(
            len(active_disabled), ', '.join(active_disabled)))

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

from plugin import alias, plugin, Platform, require


@require(platform=Platform.MACOS)
@alias("username password")
@plugin("user pass")
def user_pass(jarvis, s):

    if s == "":
        plugin_key = jarvis.input("Password for (usually one word, remember what you save it as): ")
        plugin_key = "_".join(plugin_key.split(" "))
    else:
        plugin_key = "_".join(s.split(" "))

    user, pass_word = jarvis.get_user_pass(plugin_key)
    if user is None:
        user = jarvis.input("Email/Username: ")
        pass_word = jarvis.input("", password=True)  # YOUR Password

        # SAVE credentials
        save = jarvis.input("Save Credentials (encrypted) ? (y/n) ")
        if save == 'y':
            jarvis.save_user_pass(plugin_key, user, pass_word)

    else:
        saved = jarvis.input("Use saved password for " + user + "? (y/n) ")
        if saved == 'n':
            pass_word = jarvis.input("", password=True)  # YOUR Password
            update = jarvis.input("Update password (encrypted) ? (y/n) ")
            if update == 'y':
                jarvis.update_user_pass(plugin_key, user, pass_word)

    return user, pass_word


@require(platform=Platform.MACOS)
@alias("view password")
@plugin("view pass")
def view_pass(jarvis, s):

    if s == "":
        plugin_key = jarvis.input("Password for (usually one word, remember what you save it as): ")
        plugin_key = "_".join(plugin_key.split(" "))
    else:
        plugin_key = "_".join(s.split(" "))

    user, pass_word = jarvis.get_user_pass(plugin_key)
    if user is None:
        save = jarvis.input("We do not seem to have saved username-password combination for" + plugin_key +
                            "\nWould you like to save it now? (y/n) ")
        if save == 'y':
            jarvis.internal_execute("user pass", plugin_key)

    else:
        saved = jarvis.input("View saved password for " + user + "? (y/n) ")
        if saved == 'y':
            jarvis.say("Hide your computer screen, here comes the password: " + pass_word)

            update = jarvis.input("Update password (encrypted) ? (y/n) ")
            if update == 'y':
                jarvis.internal_execute("update user pass", plugin_key)


@require(platform=Platform.MACOS)
@alias("update password")
@plugin("update pass")
def update_pass(jarvis, s):

    if s == "":
        plugin_key = jarvis.input("Password for (usually one word, remember what you save it as): ")
        plugin_key = "_".join(plugin_key.split(" "))
    else:
        plugin_key = "_".join(s.split(" "))

    user, pass_word = jarvis.get_user_pass(plugin_key)
    saved = jarvis.input("Update saved password for " + user + "? (y/n) ")
    if saved == 'y':
        pass_word = jarvis.input("", password=True)  # YOUR Password
        update = jarvis.input("Update password (encrypted) ? (y/n) ")
        if update == 'y':
            jarvis.update_user_pass(plugin_key, user, pass_word)

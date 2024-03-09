loaded_entrypoint = None


def entrypoint(fn):
    global loaded_entrypoint
    loaded_entrypoint = fn
    return fn


def get_api_key(key):
    pass

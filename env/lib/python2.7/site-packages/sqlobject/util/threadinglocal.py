try:
    from threading import local
except ImportError:
    # No threads, so "thread local" means process-global
    class local(object):
        pass

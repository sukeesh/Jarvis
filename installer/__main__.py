import traceback
try:
    from helper import log_init, log_close
    from unix_windows import IS_WIN

    log_init()

    import os
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    import steps.a_setup_virtualenv
    import steps.b_pip
    import steps.c_nltk
    if not IS_WIN:
        # TODO Optional requirements on windows
        import steps.d_optional
    import steps.e_launcher


except SystemExit:
    # Expected Error
    pass
except ImportError:
    print("\n\n")
    print("An unexpected error occurred. Please open an issue on github!")
    print("Could not import required modules.")
    print('')
    traceback.print_exc()
except OSError:
    print("\n\n")
    print("An unexpected error occurred. Please open an issue on github!")
    print("File system or OS related error occurred.")
    print('')
    traceback.print_exc()

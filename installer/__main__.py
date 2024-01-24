import traceback
from helper import log_init, log_close
from unix_windows import IS_WIN

def main():
    try:
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
    except Exception as e:
        handle_unexpected_error(e)

def handle_unexpected_error(exception):
    print("\n\n")
    print("An unexpected error occurred. Please open an issue on github!")
    print("Here is the error:")
    print('')
    traceback.print_exc()
    # You can log the exception to a file or external logging system if needed
    log_close()

if __name__ == "__main__":
    main()

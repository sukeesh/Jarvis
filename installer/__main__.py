import traceback
try:
    import installer
except SystemExit:
    # Expected Error
    pass
except:
    print("\n\n")
    print("An unexpected error occurred. Please open an issue on github!")
    print("here is the error:")
    print('')
    traceback.print_exc()

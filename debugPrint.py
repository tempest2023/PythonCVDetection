debug = False


def pr_green(msg):
    """
    print green message
    """
    print('\033[92m {}\033[00m'.format(msg))


def pr_red(msg):
    """
    print red message
    """
    print('\033[91m {}\033[00m'.format(msg))


def pr_yellow(msg):
    """
    print yellow message
    """
    print('\033[93m {}\033[00m'.format(msg))


def debug_print(message, level=1):
    """
    print debug message with different level
    level 0: red message
    level 1: yellow message
    level 2: green message
    """
    global debug
    if(debug):
        if(level == 0):
            pr_red(message)
        elif(level == 1):
            pr_yellow(message)
        else:
            pr_green(message)
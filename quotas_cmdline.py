import config
import sys

def usage_message():
    print("Usage: quotas.py <FILE> <N-SIZE> [Trimode N-sizes Phone-Email-Text] [Client]")
    print("EXAMPLE:")
    print("quota.py codesheet.txt 400 100-200-100 Tulchin")
    exit()

def parse_commandline_args():
    if (len(sys.argv) < 3 or len(sys.argv) > 5):
        print("not enough args", file=sys.stderr)
        usage_message()

    # file name
    try:
        config.filename = sys.argv[1]
        with open(config.filename, "r") as f:
            f.close()
    except FileNotFoundError:
        print("File not found, or cannot be opened", file=sys.stderr)
        usage_message()

    # n size
    try:
        config.nSize = int(sys.argv[2])
    except:
        print("N size must be a number, recieved " + sys.argv[1], file=sys.stderr)
        usage_message()

    # Trimode sizes - optional
    if (len(sys.argv) >= 4):
        if (sys.argv[3].__contains__("-")):
            try:
                config.trimode_nsize = sys.argv[3].split("-")
                for i in range(0, len(config.trimode_nsize)):
                    config.trimode_nsize[i] = int(config.trimode_nsize[i])
            except:
                print("Cannot process Trimode N sizes", file=sys.stderr)
                usage_message()
        else:
            # can be the client too, if not endsize
            config.client = sys.argv[3].lower()

    # client name - Optional
    if (len(sys.argv) == 5):
        config.client = sys.argv[4].lower()

    if (config.trimode_nsize == None):
        config.trimode_nsize = [config.nSize, config.nSize, config.nSize]
        print("\nIMPORTANT: Trimode N-sizes not defined, defaulting each to " + str(config.nSize))
        value = input("\npress any key to continue, x to exit")
        if (value == "x"):
            usage_message()

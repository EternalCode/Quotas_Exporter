import config
import sys
import argparse

def usage_message():
    print("Improper usage.")
    print("For more info:\nquota.py --help")
    exit()

def parse_commandline_args():
    # if (len(sys.argv) < 5 or len(sys.argv) > 10):
    #     print("Incorrect argument count", file=sys.stderr)
    #     usage_message()

    parser = argparse.ArgumentParser('Description=Generate CSV Quota from Codesheet')
    parser.add_argument('-f', type=str, help="Tab delimited Codesheet. |Name|Percentage|Qcode|AnsCode")
    parser.add_argument('-n', type=int, help="End size")
    parser.add_argument('-tri', type=str, help="Optional Phone-Email-Text end sizes for trisplit quotas")
    parser.add_argument('-c', type=str, help="Client name, Tulchin only right now for DNQs")
    parser.add_argument('-dual', type=str, help="Optional for dual modes, Phone-Email DNQs")
    parser.add_argument('-o', type=str, help="Optional output filename, .csv appended by default.")
    parser.add_argument('-s', type=str, help="Include splitAB splits.")
    args = parser.parse_args()


    # file name
    if (args.f != None):
        config.filename = args.f
        try:
            with open(config.filename, "r") as f:
                f.close()
        except FileNotFoundError:
            print("File: " + config.filename + " not found, or cannot be opened", file=sys.stderr)
            usage()

    # output filename
    if (args.o != None):
        config.outname = args.o + ".csv"
    else:
        config.outname = config.filename.split(".")[0] + "_quotas.csv"

    # n size
    if (args.n != None):
        config.nSize = args.n

    # n size
    if (args.n != None):
        config.nSize = args.n

    # splitab
    if (args.s != None):
        config.splitab = True

    # Trimode sizes
    if (args.tri != None):
        config.trimode_nsize = args.tri.split("-")
        for i in range(0, len(config.trimode_nsize)):
            config.trimode_nsize[i] = int(config.trimode_nsize[i])

    # dual mode sizes
    if (args.dual != None):
        config.dualmode = args.dual.split("-")
        for i in range(0, len(config.dualmode)):
            config.dualmode[i] = int(config.dualmode[i])

    #client name
    if (args.c != None):
        config.client = args.c.lower()

    to_display = "\n"

    if (config.dualmode == None):
        config.dualmode = [config.nSize, config.nSize]
        to_display += ("IMPORTANT: Dual mode N-sizes not defined, defaulting each to " + str(config.nSize))

    if (config.trimode_nsize == None):
        config.trimode_nsize = [config.nSize, config.nSize, config.nSize]
        to_display += ("\nIMPORTANT: Trimode N-sizes not defined, defaulting each to " + str(config.nSize))
    print (to_display)
    value = input("\npress any key to continue, x to exit")
    if (value == "x"):
        usage_message()

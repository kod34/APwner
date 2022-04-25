import argparse

parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required named arguments')

requiredNamed.add_argument("-H", "--handshake", action='store_true', dest="Handshake", help="Capture Handshake")
requiredNamed.add_argument("-D", "--dos", action='store_true', dest="Dos", help="DOS Attack")

args = parser.parse_args()

# Args initiate
Handshake = args.Handshake
Dos = args.Dos

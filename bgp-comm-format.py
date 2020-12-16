#!/usr/bin/env python3
#
# Messy, ham-fisted, etc.  But it seems to work.
#

import argparse
import sys

parser=argparse.ArgumentParser(description='Convert BGP raw decimal community to "new format" and vice-versa.  Doesn\'t support extended (64-bit) (yet).')
parser.add_argument('bgpcomm', type=str, help='BGP community in raw decimal OR xxxx:nnnn format.')
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args=parser.parse_args()

# Pull out bgpcommarg, make it a string for now to look for ':'
bgpcommarg = args.bgpcomm

# Conversion functions
def decimalToBinaryFourByte(n):
	binary = format(n, '032b')
	return binary

def decimalToBinaryTwoByte(n):
	binary = format(n, '016b')
	return binary

def binaryToDecimal(n): 
	return int(n,2)

# Well known communities
well_known = {
	"4294967041": "NO_EXPORT",
	"4294967042": "NO_ADVERTISE",
	"4294967043": "NO_EXPORT_SUBCONFED",
	"4294967044": "NOPEER",
}

# xxxx:nnnn argument
if ":" in bgpcommarg:
	(dec_first, dec_second) = (bgpcommarg.split(':', 2))

	dec_first = int(dec_first)
	dec_second = int(dec_second)

	# Sanity check
	if ((dec_first > 65536) or (dec_second > 65536)):
		print("Invalid value.")
		exit(1)

	bin_first = decimalToBinaryTwoByte(dec_first)
	bin_second = decimalToBinaryTwoByte(dec_second)

	bin_full = bin_first + bin_second

	dec = binaryToDecimal(bin_full)

	# Need it as string to search
	dec = str(dec)
	if dec in well_known:
		print("This is a well known community: %s" % well_known[dec])

	print(dec)

# Decimal argument
else:

	# Make it an int
	bgpcommarg = int(bgpcommarg)

	# Sanity check
	if (bgpcommarg > 4294967295):
		print("Invalid value.")
		exit(1)

	# Need it as string to search
	bgpcommarg=str(bgpcommarg)
	if bgpcommarg in well_known:
		print("This is a well known community: %s" % well_known[bgpcommarg])

	# Back to int
	bgpcommarg=int(bgpcommarg)

	bgpcommbinary = (decimalToBinaryFourByte(bgpcommarg))

	binstr=str(bgpcommbinary)

	bin_first = binstr[0:len(binstr)//2]
	bin_second = binstr[len(binstr)//2 if len(binstr)%2 == 0
		else ((len(binstr)//2)+1):]

	dec_first = binaryToDecimal(bin_first)
	dec_second = binaryToDecimal(bin_second)

	print ("%d:%d" % (dec_first, dec_second))

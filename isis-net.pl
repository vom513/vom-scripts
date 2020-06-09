#!/usr/bin/perl
#
# convert between is-is net and ip address

if (!$ARGV[0]) { print "usage: $0 (<ip address>|<is-is net>)\n"; exit 1; } 

$foo = $ARGV[0];

# ip address
if ($foo =~ /(?<!\d)(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?!\d)/g)
{
	if (
        	$1 >= 0 && $1 <= 255 &&
        	$2 >= 0 && $2 <= 255 &&
        	$3 >= 0 && $3 <= 255 &&
        	$4 >= 0 && $4 <= 255
    	) {

		# need to pad each octet with left 0's
		$o1 = sprintf "%03d", $1;
		$o2 = sprintf "%03d", $2;
		$o3 = sprintf "%03d", $3;
		$o4 = sprintf "%03d", $4;

		# need to concat all octets
		$concat = $o1.$o2.$o3.$o4;

		# need to cut by groups of 4, print out with "." between (done)
		@segments = unpack ('A4 A4 A4', $concat);		

		$isisformat = $segments[0].".".$segments[1].".".$segments[2];

		print "$isisformat\n";

		exit 0;
    	}
}

# is-is net
# Only supporting formats of: 49.0001.1720.1600.1001.00 or 1720.1600.1001

# 49.0001.1720.1600.1001.00
if ($foo =~ /^[0-9]{2}\.([0-9]{4}\.){4}[0-9]{2}$/)
{
	@segments = split(/\./, $foo);

	$concat = $segments[2].$segments[3].$segments[4];
	
	@octets = unpack ('A3 A3 A3 A3', $concat);

	$octets[0] =~ s/^\s*0+//;
	$octets[1] =~ s/^\s*0+//;
	$octets[2] =~ s/^\s*0+//;
	$octets[3] =~ s/^\s*0+//;

	print "$octets[0]\.$octets[1]\.$octets[2]\.$octets[3]\n";

	exit 0;

}

# 1720.1600.1001
if ($foo =~ /^([0-9]{4}\.){2}[0-9]{4}$/)
{
	@segments = split(/\./, $foo);

	$concat = $segments[0].$segments[1].$segments[2];
	
	@octets = unpack ('A3 A3 A3 A3', $concat);

	$octets[0] =~ s/^\s*0+//;
	$octets[1] =~ s/^\s*0+//;
	$octets[2] =~ s/^\s*0+//;
	$octets[3] =~ s/^\s*0+//;

	print "$octets[0]\.$octets[1]\.$octets[2]\.$octets[3]\n";

	exit 0;

}

print "Bad format.\n";
exit 1;

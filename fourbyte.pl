#!/usr/bin/perl
#
# convert between asplain and asdot notation

if (!$ARGV[0]) { print "usage: $0 (<4 byte dot notation>|<decimal>)\n"; exit 1; } 

$foo = $ARGV[0];

if ($foo =~ /[0-9]\.[0-9]/)
{
	($high,$low) = split (/\./, $foo);
	
	if (($high > 65535) || ($low > 65535)) { print "ASN out of range !\n"; exit 1; }

	$decimal = (($high*65536) + $low);

	print "$decimal\n";
	exit 0;
}

if ($foo =~ /[0-9]+/)
{

	if ($foo > 4294967295) { print "ASN out of range !\n"; exit 1; }

	$high = int($foo/65536);

	$low  = ($foo % 65536);

	printf "%.0f\.%d\n",$high,$low;

	exit 0;

}

print "Bad format.\n";
exit 1;

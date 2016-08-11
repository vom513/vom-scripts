#!/usr/bin/perl

use Getopt::Std;

sub ascii_to_hex ($)
{
	## Convert each ASCII character to a two-digit hex number.
	(my $str = shift) =~ s/(.|\n)/sprintf("%02lx", ord $1)/eg;
	return $str;
}

sub hex_to_ascii ($)
{
    	## Convert each two-digit hex number back to an ASCII character.
    	(my $str = shift) =~ s/([a-fA-F0-9]{2})/chr(hex $1)/eg;
    	return $str;
}

sub disclaimer ()
{
	print "*** Not all vendors implement hex/ascii wep  ***\n"; 
	print "*** conversion the same !!                   ***\n";
	print "***                                          ***\n";
	print "*** Also, you *may* need to pad strings      ***\n";
	print "*** with 0's (zeroes) to meet the length.    ***\n\n";
}

# get our two mutually exclusive options
getopts('a:h:');

# no arguments ? show usage, exit with error
if (!$opt_a && !$opt_h) { print "usage:\t$0 -a <ascii string>\n\t$0 -h <hex key>\n"; exit 1; }

# both options defined ?  exit with error
if ($opt_a && $opt_h) { print "Please use either -a OR -h.\n"; exit 1;}

# ascii case
if ($opt_a)
{
	$str = $opt_a;

	$length = length($str);
	$bits = (($length * 8) + 24);

	if (($length != 5) && ($length !=13) && ($length != 16) && ($length != 29))
	{
		print "Error: length is $length characters.\n";
		print "Key must be 5/13/16/29 ascii characters long.\n";
		exit 1;
	} 
	my $h_str = ascii_to_hex $str;
	disclaimer();
	print "hex:\t$h_str\n";
	print "$length characters, $bits bit WEP.\n";
	exit 0;
}


# hex case
if ($opt_h)
{
	$str = $opt_h;
	# strip colons from hex
	$str =~ s/\://g;

	if ($str !~ /^[0-9a-fA-F]+$/) { print "Invalid input / not hex.\n"; exit 1;}

	$length = (length($str) / 2);
	$bits = (($length * 8) + 24);

	if (($length != 5) && ($length !=13) && ($length != 16) && ($length != 29))
	{
		print "Error: length is $length bytes.\n";
		print "Key must be 5/13/16/29 bytes long.\n";
		exit 1;
	} 

	my $a_str = hex_to_ascii $str;
	disclaimer();
	print "ascii:\t$a_str\n";
	print "$length bytes, $bits bit WEP.\n";
	exit 0;
}


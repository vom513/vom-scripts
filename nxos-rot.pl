#!/usr/bin/perl

use File::Basename;
use Getopt::Std;

# nxos substitution "cipher"
@nxos_rot = (3, 22, 4, 5, 18, 0, 21, 5, 18, 3, 10, 5, 16, 22, 4, 16, 24, 17, 12, 5, 21, 18, 5, 22, 19, 7);

my $script = basename($0);

getopts('d:e:');

# no arguments ? show usage, exit with error
if (!$opt_d && !$opt_e)
{ 
	print "usage:\t$script -d <encrypted string>\n"; 
	print "\t$script -e <plaintext string>\n"; 
	exit 1; 
}

# both options defined ?  exit with error
if ($opt_d && $opt_e) { print "Please use either -d OR -e.\n"; exit 1;}

# decrypt case
if ($opt_d)
{
	$plain = $opt_d;
	nxos_decrypt($plain)
}

# encrypt case
if ($opt_e)
{
	$plain = $opt_e;
	nxos_encrypt($plain)
}

sub nxos_decrypt()
{

	$plain = @_[0];

	@input = split("", $plain);

	$index = 0;

	foreach $char(@input)
	{
		# non-letter - no change
		if ($char !~ /[a-zA-Z]/)
		{
			$enc_char = $char;
			push (@rot_complete, $enc_char);
			$index++;
			if ($index == 26) { $index = 0; };
			next;
		}
		
		# uppercase
		if ($char =~ /[A-Z]/)
		{
			$ascii = ord($char);
			$ascii_rot = ($ascii - $nxos_rot[$index]);
			if ($ascii_rot < 65)
			{
				$ascii_rot = ($ascii_rot + 26);
			}
			$enc_char = chr($ascii_rot);
			push (@rot_complete, $enc_char);
			$index++;
			if ($index == 26) { $index = 0; };
			next;
		}

		# lowercase
		$ascii = ord($char);
		$ascii_rot = ($ascii - $nxos_rot[$index]);
		if ($ascii_rot < 97)
		{
			$ascii_rot = ($ascii_rot + 26);
		}

		$enc_char = chr($ascii_rot);
		push (@rot_complete, $enc_char);

		$index++;
		if ($index == 26) { $index = 0; };
	}

	foreach $char (@rot_complete)
	{
		print $char;
	}

	print "\n";	

}

sub nxos_encrypt()
{

	$plain = @_[0];

	@input = split("", $plain);

	$index = 0;

	foreach $char(@input)
	{
		# non-letter - no change
		if ($char !~ /[a-zA-Z]/)
		{
			$enc_char = $char;
			push (@rot_complete, $enc_char);
			$index++;
			if ($index == 26) { $index = 0; };
			next;
		}
		
		# uppercase
		if ($char =~ /[A-Z]/)
		{
			$ascii = ord($char);
			$ascii_rot = ($ascii + $nxos_rot[$index]);
			if ($ascii_rot > 90)
			{
				$ascii_rot = ($ascii_rot - 26);
			}
			$enc_char = chr($ascii_rot);
			push (@rot_complete, $enc_char);
			$index++;
			if ($index == 26) { $index = 0; };
			next;
		}

		# lowercase
		$ascii = ord($char);
		$ascii_rot = ($ascii + $nxos_rot[$index]);
		if ($ascii_rot > 122)
		{
			$ascii_rot = ($ascii_rot - 26);
		}
		
		$enc_char = chr($ascii_rot);
		push (@rot_complete, $enc_char);

		$index++;
		if ($index == 26) { $index = 0; };
	}

	foreach $char (@rot_complete)
	{
		print $char;
	}

	print "\n";	

}
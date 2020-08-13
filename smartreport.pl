#!/usr/bin/env perl

use Term::ANSIColor;
use POSIX;

if ( $< != 0 )
{
	print color 'red';
	print "!! ";
	print color 'reset';

	print "This script must be run as root.";

	print color 'red';
	print " !!\n";
	print color 'reset';
 
	exit (0);
}

print "\n";

# sysctl -n kern.disks | awk '{for (i=NF; i!=0 ; i--) if(match($i, '/ada/')) print $i }' 

@uname = uname();

if ($uname[0] =~ "FreeBSD")
{
	@disks = `sysctl -n kern.disks | awk '{for (i=NF; i!=0 ; i--) if(match(\$i, '/ada/')) print \$i }'`;
}

if ($uname[0] =~ "Linux")
{
	# Check that we have lshw
	$lshw = `which lshw`;
	chomp $lshw;

	if (-x $lshw)
	{
		@disks = `sudo lshw -quiet -class disk | egrep -v 'cdrom|cdrw|dvd|sr0' | grep "logical name" | awk '{print $3}' | cut -f 3 -d '/'`;
	}
	else
	{
		print "lshw not found, please check that it is installed (and in your path).\n";
		exit (1);
	}

}

# Check that we have smartctl
$smartctl = `which smartctl`;
chomp $smartctl;

if (!-x $smartctl)
{
	print "smartctl not found, please check that it is installed (and in your path).  Package is typically \"smartmontools\" on Linux.\n";
	exit (1);
}


foreach $disk (@disks)
{
	chomp $disk;

	$snout = `smartctl -a -n standby /dev/$disk | grep ^Serial`;
	@sn = split (' ', $snout);

	$modelout = `smartctl -i /dev/$disk | grep ^Model | cut -f 2 -d : | sed 's/^[ \t]*//g'`;
	chomp $modelout;

	$deviceout = `smartctl -i /dev/$disk | grep ^Device | grep Model: | cut -f 2 -d : | sed 's/^[ \t]*//g'`;
	chomp $deviceout;

	print color 'cyan';
	print "$disk:\t";
	print color 'white';
	print "SN ";
	print color 'magenta';
	print "$sn[2]\n";
	print color 'reset';
	print color 'cyan';
	print "=================================================\n";
	print color 'reset';
	print "Model:\t\t\t$modelout\n";
	print "Device:\t\t\t$deviceout\n";

	#   5 Reallocated_Sector_Ct   0x0033   200   200   140    Pre-fail  Always       -       0
	#

	$tempout = `smartctl -a -n standby /dev/$disk | grep Temperature`;
	@temp = split(' ', $tempout);	

	# temp color codes

	print "Temperature:\t\t";

        if ($temp[9] <= 39)
        {
		print color 'green';
		print "$temp[9]";
		print color 'reset';
		print " °C\n";
	}

        if ($temp[9] > 39 && $temp[9] < 45)
        {
		print color 'yellow';
		print "$temp[9]";
		print color 'reset';
		print " °C\n";
	}

        if ($temp[9] >= 45)
        {
		print color 'red';
		print "$temp[9]";
		print color 'reset';
		print " °C\n";
	}

	$smartout = `smartctl -i -A /dev/$disk |grep -E "^  "5"|^"197"|^"198"|"FAILING_NOW"|"SERIAL""`;

	@lines = split "\n", $smartout;

	foreach $line (@lines)

	{

		@smartvals = split (' ', $line);
	
		$descr = $smartvals[1];
		$value = $smartvals[9];

		print "$descr:\t";
	
		if ($value == 0)
		{
			print color 'green';
			print "$value\n";
			print color 'reset';
		}
		else
		{
                	print color 'red';
                	print "$value\n";
                	print color 'reset';
		}

	}

	print "\n";

}

exit 0;


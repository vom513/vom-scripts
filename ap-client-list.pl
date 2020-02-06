#!/usr/bin/perl
#
# ap-client-list.pl - Gather client info from APs
# 
# Currently works on Cisco IOS Autonomous + Cisco Small Business WAP371
# (Likely to work on other similar models as well)
# 
# vom513@gmail.com / brandon@burn.net
#

use Term::ANSIColor;
use Net::SNMP;

#--------------------------------------------------------------
# BEGIN User modification settings

# Fill this in with all the APs you want to monitor
@hostnames = ('ap-basement', 'ap-groundfloor', 'ap-upstairs');

# SNMP community (global, no per-AP fanciness I'm afraid)
$community = "public";

# END User modification settings
#--------------------------------------------------------------

# Some AP's will report channel "human readable", others in MHz
%channelplan = (
2412 => 1,
2417 => 2,
2422 => 3,
2427 => 4,
2432 => 5,
2437 => 6,
2442 => 7,
2447 => 8,
2452 => 9,
2457 => 10,
2462 => 11,
2467 => 12,
2472 => 13,
2484 => 14,
5180 => 36,
5190 => 38,
5200 => 40,
5210 => 42,
5220 => 44,
5230 => 46,
5240 => 48,
5250 => 50,
5260 => 52,
5270 => 54,
5280 => 56,
5290 => 58,
5300 => 60,
5310 => 62,
5320 => 64,
5500 => 100,
5510 => 102,
5520 => 104,
5530 => 106,
5540 => 108,
5550 => 110,
5560 => 112,
5570 => 114,
5580 => 116,
5590 => 118,
5600 => 120,
5610 => 122,
5620 => 124,
5630 => 126,
5640 => 128,
5660 => 132,
5670 => 134,
5680 => 136,
5690 => 138,
5700 => 140,
5710 => 142,
5720 => 144,
5745 => 149,
5755 => 151,
5765 => 153,
5775 => 155,
5785 => 157,
5795 => 159,
5805 => 161,
5825 => 165
);

# Format is
# <mac address>	<friendly-name>
# Ex:
#
# 11:22:33:44:55:66	foobar1
#
$internal_macs = "/usr/local/etc/internal-macs.txt";

open (MACS, $internal_macs) or warn "Can't open internal macs file $internal_macs !  Devices will all output as UNKNOWN.";

while (<MACS>)
{
	$line = $_;
        next if ($line =~ /^#/);
        next if ($line =~ /^$/);
	chomp $line;
	($mac, $host) = split (' ', $line);

	$mac =~ s/://g;

	$hostdb{$mac} = $host;
}

close MACS;

foreach $hostname (@hostnames)
{
	# Cleanup
	undef @channels;

	# Open SNMP "session"
	($session,$error) = Net::SNMP->session(Hostname => $hostname, Community => $community, Version => 2);
	die "session error: $error" unless ($session);
	
	# Get sys.location
	$request = $session->get_request("1.3.6.1.2.1.1.6.0");
	if (!$request)
	{
		print color 'red';
		print "\n";
		print "Error getting sys.location from: $hostname\n";
		print $session->error."\n";
		print color 'reset';
		next;
	}
	$location = $request->{"1.3.6.1.2.1.1.6.0"};

	# Get platform
        $request = $session->get_request("1.3.6.1.2.1.47.1.1.1.1.13.1");
        die "request error: ".$session->error unless (defined $request);
        $platform = $request->{"1.3.6.1.2.1.47.1.1.1.1.13.1"};
	$platform =~ s/^\s+|\s+$//g;

	# The following section could probably be made to match "looser".  Below are simply the APs I have.

	# Cisco Small Business WAP Series
	if ($platform eq "WAP371-A-K9")
	{
		$clients_oid	= "1.3.6.1.4.1.9.6.1.104.1.7.1.1.2";
		$uptime_oid 	= "1.3.6.1.4.1.9.6.1.104.1.7.1.1.26";
		$rssi_oid	= "1.3.6.1.4.1.9.6.1.104.1.7.1.1.10";
		$channels_oid	= "1.3.6.1.4.1.9.6.1.104.1.6.1.1.17.5.119.108.97.110";
	}

	# Cisco IOS Autononmous APs
	if (($platform eq "AIR-AP1230A-A-K9") || ($platform eq "AIR-SAP2602E-A-K9") || ($platform eq "AIR-AP1142N-A-K9"))
	{
		$clients_oid 	= "1.3.6.1.4.1.9.9.273.1.2.1.1.18";
		$uptime_oid 	= "1.3.6.1.4.1.9.9.273.1.3.1.1.2";
		$rssi_oid	= "1.3.6.1.4.1.9.9.273.1.3.1.1.4";
		$channels_oid	= "1.3.6.1.4.1.9.9.272.1.1.2.5.1.3";
	}

        print "\n";
        print color 'bright_white';
        printf ("%-14s ($platform // $location)\n", $hostname);

	# Get channels table
        $channelstable = $session->get_table($channels_oid);
        die $session->{ErrorStr} if ($session->{ErrorStr});

        # Read out current channels
	# These don't sort great, especially if you have a radio (2.4 vs 5) diabled...
        print color 'white';
        print "====================================================================\n";
	print "Current frequencies:";

	print color 'cyan';

	while (my ($key,$value) = each %{$channelstable})
        {
                push (@channels, $value);
        }

	@sorted_channels = sort {$a <=> $b} (@channels);

	foreach $chanval (@sorted_channels)
	{
		# Channel is already in "human" readable format (i.e. Chan 6)
		if ($chanval < 2000) 
		{
			print " Chan. $chanval";
		}
		# Channel is Mhz (i.e. 2437) - need to look up in %channelplan
		else
		{
			print " Chan. $channelplan{$chanval}";
		}
	};

	print color 'reset';

	print "\n";

        print "--------------------------------------------------------------------\n";
	print color 'white';
	print "Client                  MAC                 RSSI  Uptime (DDD:HH:MM)\n";
	print "--------------------------------------------------------------------\n";
        print color 'reset';

	# Get client assoc table
	$clienttable = $session->get_table($clients_oid);
	die $session->{ErrorStr} if ($session->{ErrorStr});

	while (my ($key,$value) = each %{$clienttable})
	{
		push (@output, $key);
	}

	if (!@output)
	{
		print color 'white';
		print "NO CLIENTS\n";
		next;

	}

	# Get uptime table
        $uptimetable = $session->get_table($uptime_oid);
        die $session->{ErrorStr} if ($session->{ErrorStr});

	# Get rssi table
        $rssitable = $session->get_table($rssi_oid);
        die $session->{ErrorStr} if ($session->{ErrorStr});

	@sorted_output = sort @output;

	foreach $line (@sorted_output)
	{
		chomp $line;

		@oid = split (/\./, $line);
		
		$oidlength = $#oid;

		$byte1 = $oid[$oidlength - 5];
		$byte2 = $oid[$oidlength - 4];
		$byte3 = $oid[$oidlength - 3];
		$byte4 = $oid[$oidlength - 2];
		$byte5 = $oid[$oidlength - 1];
		$byte6 = $oid[$oidlength];

		$macdec = $byte1.".".$byte2.".".$byte3.".".$byte4.".".$byte5.".".$byte6;

		$mac = join(":",map{sprintf"%02x",$_}(split(/\./,$macdec)));
		$compressedmac = $mac;
		$compressedmac =~ s/://g;
		$client = $hostdb{$compressedmac};
		if (!$client) { $client = "UNKNOWN"; }

		# Search uptimetable for client
		while (my ($key,$value) = each %{$uptimetable})
        	{
			if ($key =~ m/$macdec$/) { $uptime = $uptimetable->{$key}; }
        	}

		# Search rssitable for client
		while (my ($key,$value) = each %{$rssitable})
        	{
			if ($key =~ m/$macdec$/) { $rssi = $rssitable->{$key}; }
        	}

		if (($platform eq "AIR-AP1230A-A-K9") || ($platform eq "AIR-SAP2602E-A-K9") || ($platform eq "AIR-AP1142N-A-K9"))
		{
			# convert seconds
			$uptime = convert_seconds_to_dddhhmm($uptime);
		}

		# pad days to 3 digits / leading zeroes if needed
		if (length($uptime) == 8) { $uptime = "0".$uptime; }

		print color 'magenta';
		printf("%-16s",$client);
		print "\t";
		print color 'yellow';
		printf("%-20s",$mac);
		print color 'blue';
		printf("%-4s", $rssi);
		print color 'green';
		printf("%11s", $uptime);
		print "\n";
		print color 'reset';
	}

undef @output;

$session->close;

}

print "\n";

exit 0;

# Support for human readable up to 999 days
sub convert_seconds_to_dddhhmm
{
	my $days=int($_[0]/86400);
	my $leftover=$_[0] % 86400;
	my $hours=int($leftover / 3600);
	my $leftover=$_[0] % 3600;
	my $mins=int($leftover / 60);

	return sprintf ("%03d:%02d:%02d", $days,$hours,$mins)

 }


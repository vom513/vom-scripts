#!/usr/bin/perl
#
# look up OUI vendor data from IEEE
# accepts most/any concievable input format

use Term::ANSIColor;
use File::Basename;

my $script = basename($0);

my @OUIS = ('/usr/share/misc/oui.txt', '/usr/local/etc/oui.txt');
my $OUI_URL = 'http://standards-oui.ieee.org/oui.txt';
my $ouifile;

if (!$ARGV[0]) { print "Usage: $script <mac-address>\n"; exit 1; }

$mac = $ARGV[0];

$mac = parse($mac);

if ($mac eq "INVALID") {

	print color 'bright_red';
	print "Invalid MAC !\n";
	print color 'reset';
	
	exit 1;
}

check_oui_file();

if (!$ouifile) {
        print color 'bright_red';
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
        print color 'reset';

        print "OUI file missing ! Please download.\n";
        print "Ex: ";
	print color 'cyan';
	print "\$ sudo wget -N -O /usr/local/etc/oui.txt $OUI_URL\n";
	print color 'reset';

        print color 'bright_red';
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
        print color 'reset';

	exit 1;
}

load_oui_file();

$result = get_manufactorer_for_mac($mac);

if ($age > 90) {
        print color 'bright_red';
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
        print color 'reset';

        print "OUI file is more than 90 days old, please consider updating it.\n"; 
        print "Ex: ";
	print color 'cyan';
	print "\$ sudo wget -N -O $ouifile $OUI_URL\n";
	print color 'reset';

        print color 'bright_red';
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
        print color 'reset';
        print "\n";
}

if (!$result) {
	print color 'bright_yellow';
	print "NOT FOUND\n";
	print color 'reset';
}
else
{
	print color 'bright_magenta';
	print "$result\n";
	print color 'reset';
}

print color 'faint';
print "$mac\n";
print color 'reset';

exit 0;

#
# subs below here
#
########################################################################

sub check_oui_file() {

    for my $oui_cand (@OUIS) {
        if ( -r $oui_cand) {
        $ouifile = $oui_cand;
        $age = -M $ouifile;
        last;
        }
    }
}


sub load_oui_file() {

        open (OUI, $ouifile);
        while (<OUI>) {
                $line = $_;
                if ($line =~ /^([0-9A-F]{2})-.*\(hex\)/) {

                        ($prefix, $garbage, $manu) = split (/\s+/, $line, 3);

                        # lot of bad shit in this file nowadays :(
                        $manu =~ tr/a-zA-Z0-9 .,()\/&-//dc;
                        chomp $prefix, $manu;

                        $ouihash{$prefix} = $manu;
                }
        }
        close (OUI);
}

sub get_manufactorer_for_mac() {

    my $manu = "";
    #$prefix = join('-', ($_[0] =~ /^(..):(..):(..):/));
    $prefix = $_[0];
    $prefix = uc($prefix);
    $manu = $ouihash{$prefix};
    return $manu;
}

sub parse
{
	$mac = @_[0];

	PARSE:
	{
		# *nix, etc
		# 00:01:02:03:04:05
		# 1:1:2:3:4:5
		#
		# * NOTE: macOS omits leading zeros in a given byte, need to pad those later :(
		#
		if ($mac =~ /^(([0-9a-fA-F]{1,2}):){5}[0-9a-fA-F]{1,2}$/)
		{
			@bytes = split (/:/,$mac); last PARSE;
		}
	
		# Cisco CatOS
		# 00-01-02-03-04-05
		if ($mac =~ /^(([0-9a-fA-F]{2})-){5}[0-9a-fA-F]{2}$/)
		{
			@bytes = split (/-/,$mac); last PARSE;
		}
	
		# Cisco IOS
		# 0001.0203.0405
		if ($mac =~ /^(([0-9a-fA-F]{4})\.){2}[0-9a-fA-F]{4}$/)
		{
			$mac =~ s/\.//g;
			@bytes = unpack ('A2 A2 A2 A2 A2 A2', $mac); last PARSE;
		}
	
		# Raw
		# 000102030405
        	if ($mac =~ /^[0-9a-fA-F]{12}$/)
        	{
                	@bytes = unpack ('A2 A2 A2 A2 A2 A2', $mac); last PARSE;
        	}


	# invalid format
	if (!@bytes) { return "INVALID"; }
	
	}
	
	# macOS padding
	#
	if (length($bytes[0]) == 1) { $bytes[0] = "0".$bytes[0]; }
	if (length($bytes[1]) == 1) { $bytes[1] = "0".$bytes[1]; }
	if (length($bytes[2]) == 1) { $bytes[2] = "0".$bytes[2]; }

	$oui = $bytes[0]."-".$bytes[1]."-".$bytes[2];
	$oui = lc($oui);

	return $oui;
}

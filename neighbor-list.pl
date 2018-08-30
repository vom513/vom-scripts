#!/usr/bin/perl

use Socket qw( getaddrinfo getnameinfo );
use Term::ANSIColor;

my @OUIS = ('/usr/share/misc/oui.txt', '/usr/local/etc/oui.txt');
my $OUI_URL = 'http://standards-oui.ieee.org/oui.txt';
my $oui;

@inet 	=`ip -f inet neigh | grep lladdr | sort -t . -k 1,1n -k 2,2n -k 3,3n -k 4,4n`;
@inet6	=`ip -f inet6 neigh show | grep -v ^fe80 | grep lladdr | sort`;

%ouihash;

check_oui_file();

load_oui_file();

print "\n";
print "ipv4:\n";
print "=====\n";

runlist(inet);

print "\n";
print "ipv6:\n";
print "=====\n";

runlist(inet6);

if (!$oui) {
	print "\n";

	print color 'red';
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
	print color 'reset';

	print "Please download OUI file.\n";
        print "Ex: \$ sudo wget -N -O /usr/local/etc/oui.txt $OUI_URL\n";

	print color 'red';
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
	print color 'reset';

}

if ($age > 90) {
	print "\n";

	print color 'red';
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
	print color 'reset';

	print "OUI file is more than 90 days old, please consider updating it.\n"; 
	print "Ex: \$ sudo wget -N -O $oui $OUI_URL\n";

	print color 'red';
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n";
	print color 'reset';
}

# subs below here
# ------------------------------------------------

sub runlist() {

	($af) = @_;

	foreach $line (@$af) {

	chomp $line;
	# 192.168.64.24 dev eth0.10 lladdr 78:ca:39:af:30:3e REACHABLE	
	# 2607:fcc8:8300:1f00:d0a3:637d:929:b3de dev eth0.10 lladdr 04:0c:ce:db:65:f4 REACHABLE
	($ip,$garbage,$dev,$garbage,$mac,$garbage) = split (' ', $line);
	$manuf = get_manufactorer_for_mac($mac);

	( $err, @addrs ) = getaddrinfo( $ip, 0 );
	( $err, $ptr ) = getnameinfo( $addrs[0]->{addr} );

	print color 'blue';
	printf("%-15s",$dev);

	print color 'white';
	printf("%-40s",$ip);

	print color 'yellow';
	printf("%-20s",$mac);

	print color 'cyan';
	printf("%-24s",$manuf);

	print "\n";

	if (!$ptr) { $ptr = "NO RDNS"; }

	print color 'magenta';
	print "$ptr\n";

	print color 'reset';

	print "-----------------------------------------------------------------------------------------------------\n";
	
	}
}

sub get_manufactorer_for_mac() {

    my $manu = "";
    $prefix = join('-', ($_[0] =~ /^(..):(..):(..):/));
    $prefix = uc($prefix);
    $manu = $ouihash{$prefix};
    return $manu;
}

sub check_oui_file() {

    for my $oui_cand (@OUIS) {
        if ( -r $oui_cand) {
        $oui = $oui_cand;
	$age = -M $oui;
        last;
        }
    }
}

sub load_oui_file() {

        open (OUI, $oui);
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

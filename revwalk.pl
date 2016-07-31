#!/usr/bin/perl
#
# revwalk.pl - walk through a given CIDR and lookup all PTR RR's.
# 
# vom@cinci2600.com
#
# i'm not a programmer, this can undoubtedly be improved in various ways.
# it gets the job done though.
#
# cidr calculation routines used from ipcalc - http://jodies.de/ipcalc 
#
#########################################################################

use Getopt::Std;
use Socket;
use Net::DNS;

my $thirtytwobits = 4294967295;

getopts('n:');

# basic sanity check
if (! defined ($ARGV[0])) {
	usage();
	exit 1;     
}

# get our opts (well one opt) and process/validate it
opts();

($address,$mask1) = split (/\//, $ARGV[0], 2);

# didnt get what we needed
if (!$address || !$mask1) { print "Wrong args, try again\n"; exit 1; }

# only one ?  thanks for wasting our time.
if ($mask1 == '32') { print "Umm, next time just use 'dig -x $address'.\n"; }

# convert dotted-quad etc to decimal
$address = argton($address);
$mask1 = argton($mask1);

# something too big
if ($address == '-1' || $mask1 == '-1') { print "Try a net(mask) that's not in the movie The Net.\n"; exit 1;}

# get network address
$network = $address & $mask1;

# calculate the first and last addresses in the range (including what would usually be net/bcast)
($first,$last) = calcnet($network,$mask1);

# prepend 0 to big ass numbers to make them act like strings (hack)
$first = "0".$first;
$last  = "0".$last;

main();

sub main {

# iterate through the sequence and calculate
foreach $host ($first..$last)
{
	$host=ntoa($host);

	if (!$opt_n) {

        my $res   = Net::DNS::Resolver->new(
                udp_timeout => 10,
                persistent_udp => 0,
                ); 
        my $query = $res->send("$host");


        if ($query) {
        foreach my $rr ($query->answer) {
                if ($rr->type eq "PTR") { print "$host\t", $rr->ptrdname, "\n";}
                }
        }
        $rrcount = $query->header->ancount;
        if ($rrcount == 0) { print "$host\tNONE\n"; }

	} else {

	my $res   = Net::DNS::Resolver->new(
		nameservers => [($opt_n)],
		udp_timeout => 10,
		persistent_udp => 1,
		);
	my $query = $res->send("$host");


	if ($query) {
	foreach my $rr ($query->answer) {
		if ($rr->type eq "PTR") { print "$host\t", $rr->ptrdname, "\n";}
		}
	}
	$rrcount = $query->header->ancount;
	if ($rrcount == 0) { print "$host\tNONE\n"; }
	}
}

exit 0;

}
# ---------------------------------------------------------------------

sub calcnet {
    my ($network,$mask1) = @_;
    my $hmin;
    my $hmax; 
    my $hostn;
    my $mask;

    my $broadcast = $network | ((~$mask1) & $thirtytwobits);
    
    $hmin  = $network + 1;
    $hmax  = $broadcast - 1;
    $hostn =  $hmax - $hmin + 1;
    $mask  = ntobitcountmask($mask1);
    if ($mask == 31) {
       $hmax  = $broadcast;
       $hmin  = $network;
       $hostn = 2;
    }
    if ($mask == 32) {
       $hostn = 1;
    }
        #$network = ntoa($network);
        #$hmin    = ntoa($hmin);
        #$hmax    = ntoa($hmax);
	$mask1	 = ntoa($mask1);

    if ($mask == 32) { return $network,$network; } else { return $network,$broadcast; }

}

# ------- converter ---------------------------------------------

sub bitcountmaskton 
{
   my $bitcountmask = shift;
   my $n;
   for (my $i=0;$i<$bitcountmask;$i++) {
      $n |= 1 << (31-$i);
   }
   return $n;
}

sub argton
{
   my $arg          = shift;
   my $netmask_flag = shift;
   
   my $i = 24;
   my $n = 0;
   
   # dotted decimals
   if    ($arg =~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/) {
      my @decimals = ($1,$2,$3,$4);
      foreach (@decimals) {
         if ($_ > 255 || $_ < 0) {
	    return -1;
	 }
	 $n += $_ << $i;
	 $i -= 8;
      }
      if ($netmask_flag) {
         return validate_netmask($n);
      }
      return $n;
   }
   
   # bit-count-mask (24 or /24)
   $arg =~ s/^\/(\d+)$/$1/;
   if ($arg =~ /^\d{1,2}$/) {
      if ($arg < 1 || $arg > 32) {
         return -1;
      }
      for ($i=0;$i<$arg;$i++) {
         $n |= 1 << (31-$i);
      }
      return $n;
   }
   
   # hex
   if ($arg =~   /^[0-9A-Fa-f]{8}$/ || 
       $arg =~ /^0x[0-9A-Fa-f]{8}$/  ) {
      if ($netmask_flag) {
         return validate_netmask(hex($arg));
      }
      return hex($arg);
   }

   # invalid
   return -1;
   
   sub validate_netmask
   {
      my $mask = shift;
      my $saw_zero = 0;
      # negate wildcard
      if (($mask & (1 << 31)) == 0) {
      print "WILDCARD\n";
         $mask = ~$mask;
      }
      # find ones following zeros 
      for (my $i=0;$i<32;$i++) {
         if (($mask & (1 << (31-$i))) == 0) {
            $saw_zero = 1;
         } else {
            if ($saw_zero) {
      print "INVALID NETMASK\n";
               return -1;
	    }
         }
      }
      return $mask;
   }
}

sub ntoa 
{
   return join ".",unpack("CCCC",pack("N",shift));
}

sub ntobitcountmask
{
   my $mask = shift;
   my $bitcountmask = 0;
   # find first zero
   while ( ($mask & (1 << (31-$bitcountmask))) != 0 ) {
      if ($bitcountmask > 31) {
         last;
      }
      $bitcountmask++;
   }
   return $bitcountmask;
}

sub opts {
	
	if ($opt_n && $opt_n !~ /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/) {
		($name,$aliases,$addrtype,$length,@addrs) = gethostbyname($opt_n);

		if (!@addrs) { print "Error resolving $opt_n !\n"; exit 1; }

		$nameserver = sprintf "%d.%d.%d.%d", unpack('C4',$addrs[0]);
		$opt_n = $nameserver;
	}
		
}

sub usage {
    print << "EOF";

$0 <options, see below>	<network>/<cidr mask>
                                                <network>/<dotted quad mask>
-n <name server>
	use this specific nameserver

EOF
}


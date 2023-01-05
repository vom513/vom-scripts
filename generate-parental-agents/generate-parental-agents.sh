#!/bin/sh
#
#        parental-agents "net" {
#                // net
#                192.5.6.30; 192.33.14.30; 192.26.92.30; 192.31.80.30; 192.12.94.30; 192.35.51.30; 192.42.93.30; 192.54.112.30; 192.43.172.30; 192.48.79.30; 192.52.178.30; 192.41.162.30; 192.55.83.30;
#        };
#

if [ -z "$1" ]; then
	echo "Usage: $0 <parental agents zone>"
	exit 1
fi

ZONE=$1

EMAIL="root"

FILE="/etc/bind/parental-agents-$ZONE.include"
OLDFILE="$FILE.old"
DIFF="$FILE.diff"

if [ ! -f $FILE ];then
	touch $FILE
fi

mv $FILE $OLDFILE

touch $FILE

printf "parental-agents \"$ZONE\" {\n" >> $FILE
printf "// $ZONE\n" >> $FILE

dig @localhost +short $ZONE ns | sort | while read NS
do
	A=`dig +short @localhost $NS a`
	AAAA=`dig +short @localhost $NS aaaa`

	printf "%s; %s; " $A $AAAA >> $FILE
done

printf "\n" >> $FILE
printf "};\n" >> $FILE

# Remove trailing whitespace
sed -i 's/\s*$//g' $FILE

diff $FILE $OLDFILE > $DIFF

if [ -s $DIFF ]; then
	cat $DIFF | mail -s "parental agent diffs for zone: $ZONE" $EMAIL
fi

#!/user/bin/env bash

groupadd -g 168 fuge
useradd -u 168 -g 168 -c "OpenStack Fuge Daemons" -d /var/lib/fuge fuge

mkdir -p /var/log/fuge
mkdir -p /var/lib/fuge/certificates
mkdir -p /var/run/fuge

chown fuge.fuge /var/log/fuge
chown fuge.fuge /var/lib/fuge
chown fuge.fuge /var/lib/fuge/certificates
chown fuge.fuge /var/run/fuge

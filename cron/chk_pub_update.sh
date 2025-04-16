#!/bin/bash

cmd="mosquitto_pub"
topic="system/updates/apt/"

chk=$(echo `/usr/lib/update-notifier/apt-check` ";")

reg=$(echo $chk | cut -d ';' -f 1)
sec=$(echo $chk | cut -d ';' -f 2)

echo "$chk"
echo "--"
echo "$reg"
echo "=="
echo "$sec"
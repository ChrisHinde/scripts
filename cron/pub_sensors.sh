#!/bin/bash


cmd="mosquitto_pub"
topic="system/sensors/temp/"

sens=$(sensors|awk '/C/ {print}')

while IFS= read -r line
do
    o=$(echo "$line" | grep -oP "([\w\s]+):\s+(\+[0-9]+[.][0-9]+)")
    id=$(echo "$o" | cut -d ':' -f 1)
    temp=$(echo "$o" | cut -d ':' -f 2 | xargs)

    id="${id/id /""}"
    id="${id/ /_}"

    $($cmd -t $topic$id -m $temp)

done < <(printf '%s\n' "$sens")

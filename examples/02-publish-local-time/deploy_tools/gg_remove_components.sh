#!/bin/bash
#
# Remove the Greengrass custom component: publish_time and receive_time
#
# This is used to remove components deployed locally 
# (Opposed to managing from AWS IoT Console) and is typically only used during development.
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root" 
  exit
fi

/greengrass/v2/bin/greengrass-cli deployment create \
  --remove "com.example.my_project.publish_time" \
  --remove "com.example.my_project.receive_time"
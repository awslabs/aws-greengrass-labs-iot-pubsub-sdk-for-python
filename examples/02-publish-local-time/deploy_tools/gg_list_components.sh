#!/bin/bash
#
# List all AWS IoT Greengrass components running.
#

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root" 
  exit
fi


/greengrass/v2/bin/greengrass-cli component list


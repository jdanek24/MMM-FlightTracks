#!/bin/bash

echo "Deploying MMM-FlightTracks data "
sshpass -p "pi" scp ../data/*.db pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/data

echo "Deploying MMM-FlightTracks application "
sshpass -p "pi" scp ../*.py pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/
sshpass -p "pi" scp ../*.njk pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/
sshpass -p "pi" scp ../*.js pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/
sshpass -p "pi" scp ../*.css pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/
sshpass -p "pi" scp ../.env pi@raspberrypi:/home/pi/MagicMirror/modules/MMM-FlightTracks/

# Note: this command will overwrite existing configuration file
# echo "Deploying MMM-FlightTracks config.js"
# sshpass -p "pi" scp ../config/config.js pi@raspberrypi:/home/pi/MagicMirror/config/

echo "Done"
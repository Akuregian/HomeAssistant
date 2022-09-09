#! /bin/bash

echo "Opening Webpage Interface && Starting the Docker Container";
xdg-open http://192.168.1.250:5001
docker-compose up

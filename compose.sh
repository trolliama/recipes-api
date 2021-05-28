#!/bin/bash

if [ $1 == "migrate" ]
then
echo "Migrating"
docker-compose run app sh -c "python manage.py makemigrations && python manage.py migrate"
elif [ $1 == "test" ]
then
echo "Testing"
docker-compose run app sh -c "python manage.py test && flake8"
elif [ $1 == "startapp" ]
then
echo "Creating new app"
docker-compose run app sh -c "python manage.py startapp $2"
else
echo "Initiating..."
docker-compose run app sh -c "$1"
fi

#!/bin/bash


./wait-for-it.sh db:5432 -- echo "Running entrypoint.sh"

if [ ! -f manage.py ]; then
  cd scorpio
fi

if [ ! -f scorpio/config.py ]; then
    cp scorpio/config.py.example scorpio/config.py
fi

python manage.py migrate

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8008

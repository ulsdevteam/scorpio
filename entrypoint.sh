#!/bin/bash

if [ ! -f manage.py ]; then
  cd scorpio
fi

if [ ! -f scorpio/config.py ]; then
    if [[ -n $PROD ]]; then
      envsubst < scorpio/config.py.deploy > scorpio/config.py
    else
      cp scorpio/config.py.example scorpio/config.py
    fi
fi

if [[ -n $CRON ]]; then
  cron -f -L 2
else  
  ./wait-for-it.sh $db:${SQL_PORT} -- echo "Running entrypoint.sh"
  python manage.py migrate

  #Start server
  echo "Starting server"

  #Start server
  if [[ -n $PROD ]]; then
      # Collect static files
      echo "Collecting static files"
      python manage.py collectstatic

      chmod 775 /var/www/html/scorpio/static
      chown www-data:www-data /var/www/html/scorpio/static
      apache2ctl -D FOREGROUND
  else
      python manage.py runserver 0.0.0.0:${APPLICATION_PORT}
  fi
fi
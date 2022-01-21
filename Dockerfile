FROM python:3.9

ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install --yes apache2 apache2-dev
RUN apt-get install --yes libapache2-mod-wsgi-py3
RUN apt-get -y install python3-pip
RUN pip install --upgrade pip
RUN pip install django

ADD ./apache/000-scorpio.conf /etc/apache2/sites-available/000-scorpio.conf
RUN a2dissite 000-default
RUN a2ensite 000-scorpio.conf
RUN a2enmod headers
RUN a2enmod rewrite

RUN mkdir -p /var/www/html/
COPY . /var/www/html/scorpio
WORKDIR /var/www/html/scorpio
RUN pip install -r requirements.txt
RUN ./manage.py collectstatic

RUN chmod 775 /var/www/html/scorpio
RUN chgrp www-data /var/www/html/scorpio
RUN chmod 775 /var/www/html/scorpio/static
RUN chown www-data:www-data /var/www/html/scorpio/static
RUN chmod 775 /var/www/html/scorpio/scorpio
RUN chgrp www-data /var/www/html/scorpio/scorpio

EXPOSE 8008 9201
CMD ["apache2ctl", "-D", "FOREGROUND"]

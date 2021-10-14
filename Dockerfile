FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /code/

RUN apt-get update && apt-get install cron -y
ADD /cron/scorpio_cron /etc/cron.d/scorpio_cron
RUN chmod 0644 /etc/cron.d/scorpio_cron
RUN touch /var/log/cron.log
CMD cron && tail -f /var/log/cron.log

ENTRYPOINT ["/code/entrypoint.sh"]

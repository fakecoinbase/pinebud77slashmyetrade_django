#!/bin/bash

Xvfb :99&
export DISPLAY=:99
export QT_QPA_PLATFORM=minimal

NAME="stock"
DJANGODIR=/home/pinebud/myetrade_django
SOCKFILE=${DJANGODIR}/run/gunicorn.sock
USER=pinebud
GROUP=www-data
NUM_WORKERS=2
TIME_OUT=300
DJANGO_SETTINGS_MODULE=myetrade_django.settings
DJANGO_WSGI_MODULE=myetrade_django.wsgi
PIDFILE=${DJANGODIR}/run/gunicorn.pid
LOGFILE=${DJANGODIR}/logs/myetrade.log

echo "Starting $NAME as `whoami`"

cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

RUNDIR=`dirname $SOCKFILE`
test -d $RUNDIR || mkdir -p $RUNDIR

exec /usr/local/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
	--name $NAME \
	--workers $NUM_WORKERS \
	--user=$USER --group=$GROUP \
	--bind=unix:$SOCKFILE \
	--log-level=debug \
	--timeout=$TIME_OUT \
	--pid=${PIDFILE} \
	--log-file=${LOGFILE}

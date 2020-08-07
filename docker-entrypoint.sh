#!/bin/bash
# $0 is a script name, $1, $2, $3 etc are passed arguments
# $1 is our command
# Credits: https://rock-it.pl/how-to-write-excellent-dockerfiles/
CMD=$1

wait_for_db () {
    # Wait until postgres is ready
    until nc -z $DATABASE_HOST 5432; do
        echo "$(date) - waiting for postgres... ($DATABASE_HOST:5432)"
        sleep 3
    done
}

setup_django () {
    echo Running migrations
    django-admin.py migrate --noinput

    django-admin.py createsuperuser --no-input --username admin --email admin@email.test

    echo Create cache table
    django-admin.py createcachetable
}

case "$CMD" in
    "runserver" )
        wait_for_db
        setup_django

        exec django-admin.py runserver 0.0.0.0:8080
        ;;

    "typecheck" )
        echo Running typecheck
        exec mypy .
        ;;

    "test" )
        wait_for_db

        echo Running tests
        exec pytest --ds=pipit.settings.test
        ;;

    * )
        # Run custom command. Thanks to this line we can still use
        # "docker run our_container /bin/bash" and it will work
        exec $CMD ${@:2}
        ;;
esac

#!/usr/bin/env bash
#
# Quick browser check for the Medicine Donation System microservices.
# Boots all four services plus the dev gateway and serves the whole app
# on http://localhost:8080. First run bootstraps each service's venv.
#
#   ./quick-check.sh          start everything
#   ./quick-check.sh stop     stop the services and the gateway
#   ./quick-check.sh clean    stop + delete local DBs, uploads and logs
#
# State created by a check (all gitignored):
#   <service>/db.sqlite3                             local databases
#   medicine-service/static/img/medicine_images/     uploaded images
#   search-service/unused.sqlite3                    boot placeholder
#   /tmp/mds-*.log                                   server logs
# 'clean' removes all of the above for a from-scratch next run;
# 'stop' keeps the data so you can resume where you left off.

set -u
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG=/tmp/mds
GATEWAY_URL=http://127.0.0.1:8080

SERVICES="user-service medicine-service search-service donation-service"

port_of() {
    case "$1" in
        user-service)     echo 8001 ;;
        medicine-service) echo 8002 ;;
        search-service)   echo 8003 ;;
        donation-service) echo 8004 ;;
    esac
}

has_db() { [ "$1" != "search-service" ]; }

stop_all() {
    pkill -f "manage.py runserver 127.0.0.1:800[1-4]" 2>/dev/null
    pkill -f "dev-gateway.py" 2>/dev/null
    sleep 1
    echo "stopped."
}

clean_all() {
    stop_all
    rm -f "$APP_DIR"/user-service/db.sqlite3 \
          "$APP_DIR"/medicine-service/db.sqlite3 \
          "$APP_DIR"/donation-service/db.sqlite3 \
          "$APP_DIR"/search-service/unused.sqlite3
    rm -rf "$APP_DIR"/medicine-service/static/img/medicine_images
    rm -f "$LOG"-*.log
    echo "cleaned: databases, uploaded images and logs removed."
}

start_all() {
    if curl -s -m 1 -o /dev/null "$GATEWAY_URL/health/"; then
        echo "already running at $GATEWAY_URL  (use '$0 stop' first to restart)"
        exit 0
    fi

    for svc in $SERVICES; do
        if [ ! -d "$APP_DIR/$svc/.venv" ]; then
            echo "bootstrapping $svc venv (first run only)..."
            python3 -m venv "$APP_DIR/$svc/.venv"
            "$APP_DIR/$svc/.venv/bin/pip" install -q -r "$APP_DIR/$svc/requirements.txt"
        fi
    done

    for svc in $SERVICES; do
        has_db "$svc" || continue
        (cd "$APP_DIR/$svc" && DB_ENGINE=sqlite3 .venv/bin/python manage.py migrate -v 0)
    done

    local urls="USER_SERVICE_URL=http://127.0.0.1:8001 MEDICINE_SERVICE_URL=http://127.0.0.1:8002"
    (cd "$APP_DIR/user-service" && DB_ENGINE=sqlite3 \
        nohup .venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload > "$LOG-user.log" 2>&1 &)
    (cd "$APP_DIR/medicine-service" && DB_ENGINE=sqlite3 \
        nohup .venv/bin/python manage.py runserver 127.0.0.1:8002 --noreload > "$LOG-medicine.log" 2>&1 &)
    (cd "$APP_DIR/search-service" && env $urls \
        nohup .venv/bin/python manage.py runserver 127.0.0.1:8003 --noreload > "$LOG-search.log" 2>&1 &)
    (cd "$APP_DIR/donation-service" && DB_ENGINE=sqlite3 env $urls \
        nohup .venv/bin/python manage.py runserver 127.0.0.1:8004 --noreload > "$LOG-donation.log" 2>&1 &)
    nohup python3 "$APP_DIR/dev-gateway.py" > "$LOG-gateway.log" 2>&1 &

    for svc in $SERVICES; do
        port=$(port_of "$svc")
        up=0
        for _ in $(seq 1 30); do
            curl -s -m 1 -o /dev/null "http://127.0.0.1:$port/health/" && up=1 && break
            sleep 0.5
        done
        [ $up = 1 ] || { echo "ERROR: $svc failed to start - see $LOG-*.log"; exit 1; }
    done
    curl -s -m 2 -o /dev/null "$GATEWAY_URL/health/" \
        || { echo "ERROR: gateway failed to start - see $LOG-gateway.log"; exit 1; }

    cat <<EOF

  App running:  $GATEWAY_URL
  Logs:         $LOG-*.log

  When you're done:
    $0 stop     # stop processes, keep your data for next time
    $0 clean    # stop + wipe databases, uploads and logs
EOF
}

case "${1:-start}" in
    start) start_all ;;
    stop)  stop_all ;;
    clean) clean_all ;;
    *) echo "usage: $0 [start|stop|clean]"; exit 1 ;;
esac

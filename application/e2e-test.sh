#!/usr/bin/env bash
#
# End-to-end test for the microservice split of the Medicine Donation System.
#
# Expects all four services to be running (see application/README.md):
#   user-service      $USER_URL      (default http://127.0.0.1:8001)
#   medicine-service  $MEDICINE_URL  (default http://127.0.0.1:8002)
#   search-service    $SEARCH_URL    (default http://127.0.0.1:8003)
#   donation-service  $DONATION_URL  (default http://127.0.0.1:8004)
#
# Drives the full user journey with curl: registration, login, medicine
# CRUD (incl. image upload), NGO/priority search, the donation lifecycle
# (request -> accept -> complete, and reject), health probes, internal API
# token enforcement, and logout.
#
# The services must share one hostname (cookies are host-scoped); locally
# they run on different ports of 127.0.0.1, which browsers and curl treat
# as one cookie domain.

set -u

USER_URL=${USER_URL:-http://127.0.0.1:8001}
MEDICINE_URL=${MEDICINE_URL:-http://127.0.0.1:8002}
SEARCH_URL=${SEARCH_URL:-http://127.0.0.1:8003}
DONATION_URL=${DONATION_URL:-http://127.0.0.1:8004}
INTERNAL_API_TOKEN=${INTERNAL_API_TOKEN:-insecure-internal-token}

# Gateway mode: all four URLs point at one host (e.g. dev-gateway.py or the
# cluster ingress), which routes by path prefix and hides /api/*.
GATEWAY_MODE=0
[ "$USER_URL" = "$MEDICINE_URL" ] && GATEWAY_MODE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPLOAD_IMG="$SCRIPT_DIR/medicine-service/static/img/favicon.png"

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT
JAR_DONOR="$WORK_DIR/donor.jar"
JAR_NGO="$WORK_DIR/ngo.jar"

PASS_DONOR='GreenMedix#2026'
PASS_NGO='BlueClinic#2026'
STAMP=$(date +%s)
DONOR_USER="donor_$STAMP"
NGO_USER="ngo_$STAMP"
NGO_FULLNAME="Health Care NGO $STAMP"
DONOR_FULLNAME="Donor One $STAMP"

STEP_NO=0

step() {
    STEP_NO=$((STEP_NO + 1))
    echo "--- [$STEP_NO] $1"
}

fail() {
    echo "FAILED at step $STEP_NO: $1" >&2
    exit 1
}

contains() { # haystack-file needle
    grep -q "$2" "$1" || fail "expected to find '$2' in $1"
}

csrf_from() { # jar url -> token on stdout
    curl -s -c "$1" -b "$1" "$2" |
        grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' |
        head -1 | cut -d'"' -f4
}

expect_code() { # expected actual context
    [ "$1" = "$2" ] || fail "$3 (expected HTTP $1, got $2)"
}

# ---------------------------------------------------------------- health
if [ "$GATEWAY_MODE" = 1 ]; then
    step "health endpoint answers through the gateway"
    body=$(curl -s "$USER_URL/health/")
    echo "$body" | grep -q '"status": "healthy"' || fail "gateway health: $body"
else
    step "health endpoints answer on all four services"
    for svc in "$USER_URL user-service" "$MEDICINE_URL medicine-service" \
               "$SEARCH_URL search-service" "$DONATION_URL donation-service"; do
        set -- $svc
        body=$(curl -s "$1/health/")
        echo "$body" | grep -q '"status": "healthy"' || fail "$2 unhealthy: $body"
        echo "$body" | grep -q "\"service\": \"$2\"" || fail "$2 wrong identity: $body"
    done
fi

# ------------------------------------------------------------- register
step "register donor account (user-service)"
CSRF=$(csrf_from "$JAR_DONOR" "$USER_URL/accounts/register/")
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/reg1.html" -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "username=$DONOR_USER" \
    --data-urlencode "email=$DONOR_USER@example.com" \
    --data-urlencode "password1=$PASS_DONOR" \
    --data-urlencode "password2=$PASS_DONOR" \
    --data-urlencode "fullname=$DONOR_FULLNAME" \
    --data-urlencode "identity=1234567890" \
    --data-urlencode "phone=01711111111" \
    "$USER_URL/accounts/register/")
expect_code 302 "$code" "donor registration"

step "register NGO account (user-service)"
CSRF=$(csrf_from "$JAR_NGO" "$USER_URL/accounts/register/")
code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/reg2.html" -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "username=$NGO_USER" \
    --data-urlencode "email=$NGO_USER@example.com" \
    --data-urlencode "password1=$PASS_NGO" \
    --data-urlencode "password2=$PASS_NGO" \
    --data-urlencode "is_ngo=on" \
    --data-urlencode "fullname=$NGO_FULLNAME" \
    --data-urlencode "identity=0987654321" \
    --data-urlencode "phone=01722222222" \
    "$USER_URL/accounts/register/")
expect_code 302 "$code" "NGO registration"

# ---------------------------------------------------------------- login
step "login donor; session cookie works on medicine-service"
CSRF=$(csrf_from "$JAR_DONOR" "$USER_URL/accounts/login/")
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "username=$DONOR_USER" \
    --data-urlencode "password=$PASS_DONOR" \
    "$USER_URL/accounts/login/")
expect_code 302 "$code" "donor login"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/dash_donor.html" "$MEDICINE_URL/"
contains "$WORK_DIR/dash_donor.html" "Medicine List"
contains "$WORK_DIR/dash_donor.html" "Prioritized Search"   # donor-only navbar entry

step "login NGO; session cookie works on medicine-service"
CSRF=$(csrf_from "$JAR_NGO" "$USER_URL/accounts/login/")
code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o /dev/null -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "username=$NGO_USER" \
    --data-urlencode "password=$PASS_NGO" \
    "$USER_URL/accounts/login/")
expect_code 302 "$code" "NGO login"
curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/dash_ngo.html" "$MEDICINE_URL/"
contains "$WORK_DIR/dash_ngo.html" "Medicine List"

# ------------------------------------------------------ medicine (NGO)
step "NGO adds two needed medicines (medicine-service)"
for med in "Napa 500 3 100" "Seclo 20 2 50"; do
    set -- $med
    CSRF=$(csrf_from "$JAR_NGO" "$MEDICINE_URL/add-medicine/")
    code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o /dev/null -w '%{http_code}' \
        --data-urlencode "csrfmiddlewaretoken=$CSRF" \
        --data-urlencode "MedicineName=$1" \
        --data-urlencode "DosageAmount=$2" \
        --data-urlencode "MedicinePriority=$3" \
        --data-urlencode "AmountRequired=$4" \
        "$MEDICINE_URL/add-medicine/")
    expect_code 302 "$code" "NGO add medicine $1"
done
curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/ngo_list.html" "$MEDICINE_URL/edit-list/"
contains "$WORK_DIR/ngo_list.html" "Napa"
contains "$WORK_DIR/ngo_list.html" "Seclo"

# ----------------------------------------------------- medicine (donor)
step "donor adds a medicine with an expiry-date image upload"
[ -f "$UPLOAD_IMG" ] || fail "test image not found: $UPLOAD_IMG"
CSRF=$(csrf_from "$JAR_DONOR" "$MEDICINE_URL/add-medicine/")
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' \
    -F "csrfmiddlewaretoken=$CSRF" \
    -F "MedicineName=Napa" \
    -F "DosageAmount=500" \
    -F "PillsLeft=30" \
    -F "ExpiryDateImage=@$UPLOAD_IMG;type=image/png" \
    "$MEDICINE_URL/add-medicine/")
expect_code 302 "$code" "donor add medicine with image"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/donor_list.html" "$MEDICINE_URL/edit-list/"
contains "$WORK_DIR/donor_list.html" "Napa"
contains "$WORK_DIR/donor_list.html" "medicine_images"      # uploaded image path

# ---------------------------------------------------------------- search
step "NGO name search (search-service -> user-service API)"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/search.html" \
    "$SEARCH_URL/search/ngo_search/Health/"
contains "$WORK_DIR/search.html" "$NGO_FULLNAME"

step "priority search (search-service -> medicine + user APIs)"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/priority.html" \
    "$SEARCH_URL/search/priority_search/medicine/"
contains "$WORK_DIR/priority.html" "$NGO_FULLNAME"
NGO_ID=$(grep -oE 'donation_request/[0-9]+/' "$WORK_DIR/priority.html" | head -1 | grep -oE '[0-9]+')
[ -n "$NGO_ID" ] || fail "could not extract NGO id from priority search page"

step "NGO medicine list page (search-service)"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/ngo_meds.html" \
    "$SEARCH_URL/search/show_ngo_list/$NGO_ID/"
contains "$WORK_DIR/ngo_meds.html" "Napa"
contains "$WORK_DIR/ngo_meds.html" "$NGO_FULLNAME"

# -------------------------------------------------------------- donation
step "donor sends a donation request (donation-service)"
CSRF=$(csrf_from "$JAR_DONOR" "$DONATION_URL/donations/donation_request/$NGO_ID/")
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "Delivery_type=Pick-up" \
    --data-urlencode "Pick_up_address=123 Test Street" \
    "$DONATION_URL/donations/donation_request/$NGO_ID/")
expect_code 302 "$code" "donation request"

step "NGO sees the request with denormalized donor details"
curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/notif_ngo.html" \
    "$DONATION_URL/donations/ngo_notification/"
contains "$WORK_DIR/notif_ngo.html" "$DONOR_FULLNAME"
REQ_ID=$(grep -oE 'donation_details/[0-9]+/' "$WORK_DIR/notif_ngo.html" | head -1 | grep -oE '[0-9]+')
[ -n "$REQ_ID" ] || fail "could not extract donation request id"

step "NGO accepts with pick-up date/time"
CSRF=$(csrf_from "$JAR_NGO" "$DONATION_URL/donations/donation_details/$REQ_ID/")
code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o /dev/null -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "pickupDate=2026-08-01" \
    --data-urlencode "pickupTime=10:30" \
    "$DONATION_URL/donations/donation_details/$REQ_ID/")
expect_code 302 "$code" "accept donation"
curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/notif_ngo2.html" \
    "$DONATION_URL/donations/ngo_notification/"
contains "$WORK_DIR/notif_ngo2.html" "01711111111"          # donor phone, denormalized
contains "$WORK_DIR/notif_ngo2.html" "complete/$REQ_ID/"

step "donor sees the accepted request"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/notif_donor.html" \
    "$DONATION_URL/donations/ngo_notification/"
contains "$WORK_DIR/notif_donor.html" "$NGO_FULLNAME"
contains "$WORK_DIR/notif_donor.html" "Accepted"

step "NGO marks the donation complete"
code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o /dev/null -w '%{http_code}' \
    "$DONATION_URL/donations/complete/$REQ_ID/")
expect_code 302 "$code" "complete donation"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/notif_donor2.html" \
    "$DONATION_URL/donations/ngo_notification/"
contains "$WORK_DIR/notif_donor2.html" "Completed"

step "second request can be rejected"
CSRF=$(csrf_from "$JAR_DONOR" "$DONATION_URL/donations/donation_request/$NGO_ID/")
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" \
    --data-urlencode "Delivery_type=In-person" \
    --data-urlencode "Pick_up_address=" \
    "$DONATION_URL/donations/donation_request/$NGO_ID/")
expect_code 302 "$code" "second donation request"
curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o "$WORK_DIR/notif_ngo3.html" \
    "$DONATION_URL/donations/ngo_notification/"
REQ2_ID=$(grep -oE 'reject/[0-9]+/' "$WORK_DIR/notif_ngo3.html" | head -1 | grep -oE '[0-9]+')
[ -n "$REQ2_ID" ] || fail "could not extract second request id"
code=$(curl -s -b "$JAR_NGO" -c "$JAR_NGO" -o /dev/null -w '%{http_code}' \
    "$DONATION_URL/donations/reject/$REQ2_ID/")
expect_code 302 "$code" "reject donation"
curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o "$WORK_DIR/notif_donor3.html" \
    "$DONATION_URL/donations/ngo_notification/"
contains "$WORK_DIR/notif_donor3.html" "Rejected"

# ------------------------------------------------------------- internals
if [ "$GATEWAY_MODE" = 1 ]; then
    step "internal APIs are not exposed through the gateway"
    code=$(curl -s -o /dev/null -w '%{http_code}' "$USER_URL/api/ngos/")
    expect_code 404 "$code" "gateway must not route /api/*"
    code=$(curl -s -o /dev/null -w '%{http_code}' "$MEDICINE_URL/api/medicines/ngo/")
    expect_code 404 "$code" "gateway must not route /api/*"
else
    step "internal APIs reject calls without the shared token"
    code=$(curl -s -o /dev/null -w '%{http_code}' "$USER_URL/api/ngos/")
    expect_code 403 "$code" "user-service API without token"
    code=$(curl -s -o /dev/null -w '%{http_code}' "$MEDICINE_URL/api/medicines/ngo/")
    expect_code 403 "$code" "medicine-service API without token"
    code=$(curl -s -o /dev/null -w '%{http_code}' \
        -H "X-Internal-Token: $INTERNAL_API_TOKEN" "$USER_URL/api/ngos/")
    expect_code 200 "$code" "user-service API with token"
fi

# ----------------------------------------------------------------- logout
step "logout invalidates the session on every service"
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' \
    "$USER_URL/accounts/logout/")
expect_code 302 "$code" "logout"
code=$(curl -s -b "$JAR_DONOR" -c "$JAR_DONOR" -o /dev/null -w '%{http_code}' "$MEDICINE_URL/")
expect_code 302 "$code" "dashboard after logout should redirect to login"

echo
echo "ALL $STEP_NO STEPS PASSED"

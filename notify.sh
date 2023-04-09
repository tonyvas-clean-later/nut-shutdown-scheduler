#!/usr/bin/bash

WEBHOOK_URL="https://trigger.macrodroid.com/d1468e83-8094-4d1d-a34e-eaa3117d5cad/notifier2"

title=$1
content=$2
time_sent=$(date +%s)

if [[ $title == '' ]]; then content='Untitled'; fi
if [[ $content == '' ]]; then content='No content'; fi

curl -G "${WEBHOOK_URL}" \
  --data-urlencode "title=${title}" \
  --data-urlencode "content=${content}" \
  --data-urlencode "time=${time_sent}"
#!/bin/bash -x


PAYLOAD=$(cat <<EOF
{  "eventType": "CUSTOM_ANNOTATION",
  "entitySelector":
     "type($1), tag($2)",
  "title":"\"$3\"",
  "properties" : {
  "JenkinsJobName" : "$4",
  "BuildUrl" : "$6",
  "Description": "$5",
  "BuildVersion":"${9}",
  "Timestamp":"$(date --utc +%FT%T.000000000Z)"
  }
}
EOF
)
echo $PAYLOAD

curl -X 'POST' \
     "${DT_URL}/api/v2/events/ingest/" \
     -H "accept: application/json; charset=utf-8" \
     -H "Content-Type: application/json; charset=utf-8" \
     -H "Authorization: Api-Token ${DT_TOKEN}" \
     -d "${PAYLOAD}"

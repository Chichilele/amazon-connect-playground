#!/bin/bash
set -eo pipefail
export AWS_PROFILE='barclays-sandbox'
FUNCTION='s3-to-connect'

## compile and package
echo '-----------------'
echo 'build and package...'
echo '-----------------'
GOARCH=amd64 GOOS=linux go build -o bin/main src/go/main.go && zip -j bin/main.zip bin/main

echo '-----------------'
echo 'deploy...'
echo '-----------------'
aws lambda update-function-code     \
    --function-name $FUNCTION       \
    --zip-file fileb://bin/main.zip | tee

echo '-----------------'
echo 'test...'
echo '-----------------'

aws lambda invoke                           \
    --function-name $FUNCTION               \
    --cli-binary-format raw-in-base64-out   \
    --payload file://input_data/update_event.json      \
    out.json                                    | tee

cat out.json
rm out.json
#!/bin/bash

cd /home/ubuntu/.wg++/
./run.sh

sed -i -E "s/\W\(\?\)\W*<\/title>/\<\/title>/" guide.xml
aws s3api put-object --acl public-read --bucket iptvbr --key epg.xml --body /home/ubuntu/.wg++/guide.xml

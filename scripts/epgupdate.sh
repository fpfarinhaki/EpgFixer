#!/bin/bash

wget http://mtvs.me/j3xGPzYB -O /home/ubuntu/github/EpgFixer/iptv.m3u

cd /home/ubuntu/github/EpgFixer/
python3 main.py iptv.m3u

aws s3api put-object --acl public-read --bucket iptvbr --key channels.m3u --body /home/ubuntu/github/EpgFixer/channels.m3u
aws s3api put-object --acl public-read --bucket iptvbr --key movies.m3u --body /home/ubuntu/github/EpgFixer/movies.m3u
aws s3api put-object --acl public-read --bucket iptvbr --key series.m3u --body /home/ubuntu/github/EpgFixer/series.m3u

cd /home/ubuntu/.wg++/
./run.sh

sed -i -E "s/\W\(\?\)\W*<\/title>/\<\/title>/" guide.xml
aws s3api put-object --acl public-read --bucket iptvbr --key epg.xml --body /home/ubuntu/.wg++/guide.xml





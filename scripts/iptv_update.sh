#!/bin/bash

wget http://mtvs.me/j3xGPzYB -O ~/github/EpgFixer/test.m3u

cd ~/github/EpgFixer/
python3 main.py

aws s3api put-object --acl public-read --bucket iptvbr --key lista_vod.m3u --body ~/github/EpgFixer/playlist_vod.m3u
aws s3api put-object --acl public-read --bucket iptvbr --key lista_tv.m3u --body ~/github/EpgFixer/playlist.m3u

cd ~/.wg++/
./run.sh

sed -i -E "s/\W\(\?\)\W*<\/title>/\<\/title>/" guide_mi.xml
aws s3api put-object --acl public-read --bucket iptvbr --key epg.xml --body ~/.wg++/guide_mi.xml





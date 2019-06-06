#!/bin/bash
FILENAME=iptv.m3u

cd /home/ubuntu/m3u_list_manager
wget http://mtvs.me/j3xGPzYB -O /home/ubuntu/m3u_list_manager/$FILENAME
m3ulistmanager --m3u-file $FILENAME

aws s3api put-object --acl public-read --bucket iptvbr --key channels.m3u --body /home/ubuntu/m3u_list_manager/channels.m3u
aws s3api put-object --acl public-read --bucket iptvbr --key movies.m3u --body /home/ubuntu/m3u_list_manager/movies.m3u
aws s3api put-object --acl public-read --bucket iptvbr --key series.m3u --body /home/ubuntu/m3u_list_manager/series.m3u


#!/bin/bash

sudo pyinstaller ./application/M3uListManager.py --distpath /usr/local/bin/ --clean -F -n m3ulistmanager --exclude-module test

sudo pyinstaller ./application/ManualFixer.py --distpath ~/m3u_list_manager/ --clean -F -n manualfixer --exclude-module test

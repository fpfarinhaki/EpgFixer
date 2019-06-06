#!/bin/bash

sudo pyinstaller ./application/M3uListManager.py --distpath /usr/local/bin/ --clean -F -n m3ulistmanager --exclude-module test
#!/bin/bash

ipfs daemon &

if [ -z "$CID" ]; then
  python watcher.py
else
  python cli.py
fi

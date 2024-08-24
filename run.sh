#!/bin/bash

ipfs daemon &
python watcher.py

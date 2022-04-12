#!/bin/bash

apt-get update
apt-get install openslide-tools
pip install gdown
pip install wholeslidedata
python ./downloaddata.py


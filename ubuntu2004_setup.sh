#!/bin/bash

apt-get update
apt-get install openslide-tools
pip install gdown
pip install black
pip install --upgrade --no-cache-dir gdown
pip install wholeslidedata
python ./pathology-whole-slide-data/downloaddata.py
cp ./pathology-whole-slide-data/docs/userguide/configs/ ./


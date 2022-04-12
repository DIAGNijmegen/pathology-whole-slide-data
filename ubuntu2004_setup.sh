#!/bin/bash

apt-get update
apt-get install openslide-tools
pip install gdown
pip install wholeslidedata
python ./pathology-whole-slide-data/download_data.py


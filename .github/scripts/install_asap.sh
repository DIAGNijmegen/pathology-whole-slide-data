#!/bin/sh

apt-get update 
apt-get -y install curl 
curl --remote-name --location "https://github.com/computationalpathologygroup/ASAP/releases/download/ASAP-2.1-(Nightly)/ASAP-2.1-Ubuntu2004.deb" 
dpkg --install ASAP-2.1-Ubuntu2004.deb || true 
apt-get -f install --fix-missing --fix-broken --assume-yes 
ldconfig -v 
apt-get clean 
echo "/opt/ASAP/bin" > /home/runner/.local/lib/python3.8/site-packages/asap.pth 
rm ASAP-2.1-Ubuntu2004.deb
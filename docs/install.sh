

export asap_version=1.9
export asap_deb=ASAP-${asap_version}-Linux-Ubuntu1804.deb
curl --remote-name --location https://github.com/computationalpathologygroup/ASAP/releases/download/${asap_version}/${asap_deb}
sudo apt-get update
sudo dpkg --install ${asap_deb} || true
sudo apt-get install --fix-broken --assume-yes
sudo ldconfig -v 
echo python -m site
echo "/opt/ASAP/bin" > /usr/local/lib/python3.8/dist-packages/asap.pth 

sudo apt-get install openslide-tools
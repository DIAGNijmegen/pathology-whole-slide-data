import subprocess
import sys
from pathlib import Path

from black import main

try:
    import gdown
except ImportError:
    raise ImportError('gdown not installed. Install gdown with pip or use install_gdown() from downloaddata.py')

WSI_DOWNLOAD_LINK = "https://drive.google.com/uc?id=1noRtbC5fxBlnO7YnvktjIDhFI61PdOSB"
WSI_NAME = Path("TCGA-21-5784-01Z-00-DX1.tif")

WSA_DOWNLOAD_LINK = "https://drive.google.com/uc?id=1jkTp0IJHHpmLd1yDO1L3KRFJgm0STh0d"
WSA_NAME = Path("TCGA-21-5784-01Z-00-DX1.xml")

WSM_DOWNLOAD_LINK = "https://drive.google.com/uc?id=1nLdKzSLq79mon1RCevgEmG59E8Oq9JhZ"
WSM_NAME = Path("TCGA-21-5784-01Z-00-DX1_tb_mask.tif")

def _download(output_folder, download_link, name):
    output_path = Path(output_folder) / name
    if not output_path.exists():
        gdown.download(download_link, str(output_path))

def install_gdown():
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "gdown"], stdout=subprocess.DEVNULL
    )

def download_example_data(output_folder=Path("/tmp/")):
    _download(output_folder, WSI_DOWNLOAD_LINK, WSI_NAME)
    _download(output_folder, WSA_DOWNLOAD_LINK, WSA_NAME)
    _download(output_folder, WSM_DOWNLOAD_LINK, WSM_NAME)



if __name__ == "__main__":
    download_example_data()
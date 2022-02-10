from pathlib import Path

_WSI_DOWNLOAD_LINK = 'https://drive.google.com/uc?id=1noRtbC5fxBlnO7YnvktjIDhFI61PdOSB'
_WSI_NAME = Path('TCGA-21-5784-01Z-00-DX1.tif')

_WSA_DOWNLOAD_LINK = 'https://drive.google.com/uc?id=1jkTp0IJHHpmLd1yDO1L3KRFJgm0STh0d'
_WSA_NAME = Path('TCGA-21-5784-01Z-00-DX1.xml')

import gdown


def _download(output_folder, download_link, name):
    output_path = Path(output_folder) / name
    if not output_path.exists():
        gdown.download(download_link, str(output_path))
    return str(output_path)


def download_wsi(output_folder):
    return _download(output_folder, _WSI_DOWNLOAD_LINK, _WSI_NAME)


def download_wsa(output_folder):
    return _download(output_folder, _WSA_DOWNLOAD_LINK, _WSA_NAME)


def download(output_folder):
    return download_wsi(output_folder), download_wsa(output_folder)

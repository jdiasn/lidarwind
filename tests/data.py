import os
import gdown
import shutil
import glob
import pytest



def get_sample_data(sample_path, file_type):

    if file_type == "12-00":
        url = "https://drive.google.com/uc?export=download&id=1i6iX6KuZOkP_WLuPZHG5uCcvRjlWS-SU"

    if file_type == "dbs":
        url = "path"

    output = f"{sample_path}{file_type}.zip"
    gdown.download(url, output, quiet=False)

    print(f"Extracting: {output}")
    shutil.unpack_archive(output, sample_path)
    os.remove(output)

#!/usr/bin/env python3
"""
    demonstrate downloading a large file with a progressbar
"""

import progressbar
import requests

Verbose = False


def download(url, target):
    """
    Loosely inspired by:

    https://towardsdatascience.com/how-to-download-files-using-python-part-2-19b95be4cdb5
    and
    progressbar2 examples

    Downloads url to a named file with progress bar

    :param url: url to download
    :param target:  filename to save to
    :return: nothing
    """

    name = url.split('/')[-1]

    if Verbose:
        print(f"[info] Downloading {name}")

    # if the server doesn't give us a content-length, we will get an error here.  ooops.
    r = requests.get(url, stream=True, allow_redirects=True)
    total_size = int(r.headers.get('content-length'))

    widgets = [
        target + ":",
        ' ', progressbar.Percentage(),
        ' ', progressbar.Bar(),
        ' ', progressbar.ETA(),
        ' ', progressbar.FileTransferSpeed(),
    ]

    location = 0

    with progressbar.ProgressBar(widgets=widgets, max_value=total_size).start() as bar, \
         open(target, 'wb') as f:
        for ch in r.iter_content(chunk_size=1024):
            if ch:
                if location <= total_size:
                    bar.update(location)

                f.write(ch)
                location += len(ch)


if __name__ == "__main__":
    download(
        "https://gis.data.cnra.ca.gov/datasets/CALFIRE-Forestry::2000s-2.geojson?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D",
        "CALFIRE.geojson"
    )
    """
    # very large file to play with
    download(
        "http://resources.mpi-inf.mpg.de/yago-naga/yago3.1/yago3.1_entire_ttl.7z",
        "yago3.1.7z"
    )
    """

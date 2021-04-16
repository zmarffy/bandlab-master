# `bandlab-master`

`bandlab-master` is a Python script that uploads a song to your [BandLab](https://www.bandlab.com/) account, masters it with default settings, and downloads it as WAV. Eventually, I will update this to delete the temporary project once its master downloads.

`balndlab-master` uses my amazingly clever (and probably terrible) [`webdriver-extended`](https://github.com/zmarffy/webdriver-extended).

## Requirements

* Chromium/Google Chrome
* `chromedriver`

## Usage

`bandlab-master [file_to_master]`

(Wow, that was confusing.)

Make sure your BandLab credentials are in `~/.bandlab/.creds`, username on first line and password on second.

# `bandlab-master`

`bandlab-master` is a Python script that uploads a song to your [BandLab](https://www.bandlab.com/) account, masters it with default settings, and downloads it as WAV.

## Requirements

* `chromium`
* `chromedriver`
* `selenium` (a `pip` package)
* `webdriver-extended` (a `pip` package)
* `zmtools` (a `pip` package)

**Note:** It is unknown how well this works if installed via the DEB file due to dependencies. I think you may need to use the non-snap version of Chromium. This will be addressed in the future.

## Usage

`bandlab-master [file_to_master]`

Make sure your BandLab credentials are in `~/.bandlab/.creds`, username on first line and password on second.

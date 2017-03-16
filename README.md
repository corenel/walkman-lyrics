# Walkman Lyrics
A tiny script to download lyrics for Walkman.
## Install
```bash
# Install requirements
$ pip3 install requests tinytag pycrypto
```

## Usage
```bash
$ python3 test.py [-h] [-m {trans,original,both}] [-f FORMAT] [-q] [-d] [-w] path
```

* Positional arguments:
  * `path`: Root path for Walkman, e.g. `/Volumes/SD_CARD/MUSIC/`
* Optional arguments:
  * `-h`, `--help`: Show help message and exit
  * `-m {trans,original,both}`, `--mode {trans,original,both}`: Mode of LRC file
    * `trans`: only save translated lyrics
    * `original`: only save original lyrics
    * `both`: save both original and translated lyrics. Lyrics format is set by `-f` or -`-format`.
  * `-f FORMAT`, `--format FORMAT`: Format to combine both types of lyrics
    * Default: `'{orig} / {trans}'`
  * `-q`, `--quiet`: Quiet mode, no prompt output and choose first search result by default.
  * `-d`, `--default`: Choose first search result by default.
  * `-w`, `--overwrite`: Overwrite existed lyrics

## Acknowledgement
This script is inspired by:
* [netease_music_lyric](https://github.com/liuxueyang/netease_music_lyric)
* [Netease LRC Downloader](https://gist.github.com/blueset/43172f5ecd32e75d9f9bc6b7e0177755)

# Bandcamp-Downloader
Bandcamp Downloader in python

## Instructions

### Permission to execute the file
`chmod +x bdcamp.py`

### Usage
```bash 
./bdcamp.py -h
usage: bdcamp.py [-h] [-v] [-n] [-a] music_url

positional arguments:
  music_url        Bandcamp Song URL

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    increase output verbosity
  -n, --noconfirm  do not ask for confirmation
  -a, --all        download everything
```

### Example
`./bdcamp.py https://lostinmadrid.bandcamp.com/album/1st-e-p` will create a folder named 1st-ep and download all the songs of that album, present on the bandcamp url provided, in that folder. This folder will be created in the same folder from where the script is being executed.

## Features

> Download all songs of an artist given the url (`artist.bandcamp.com/music`)

> Download a complete album given the url (`artist.bandcamp.com/album/album-name`)

> Download a single track given the url (`artist.bandcamp.com/track/track-name`)

## TODO

> Implement regex input or a better way to help user select songs from the list instead of providing comma separated list.

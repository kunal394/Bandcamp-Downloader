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

> Download a complete album given the url
> Download a single track given the url

## Features to be implemented

> Download all the songs of an artist given the bandcamp url of that artist

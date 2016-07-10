[![MIT Licence](https://badges.frapsoft.com/os/mit/mit-175x39.png?v=103)](https://opensource.org/licenses/mit-license.php)
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source-175x29.png?v=103)](https://github.com/ellerbrock/open-source-badge/)

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
`./bdcamp.py https://randartist.bandcamp.com/album/first-album` will create a folder named `First Album` and download all the
songs of that album, present on the bandcamp url provided, in that folder and this folder will be inside a folder named
`Rand Artist` (if that is the artist name provide on the artist page). The artist's folder will be present inside the current folder.

## Features

> Download all songs of an artist given the url (`artist.bandcamp.com/music`)

> Download a complete album given the url (`artist.bandcamp.com/album/album-name`)

> Download a single track given the url (`artist.bandcamp.com/track/track-name`)

## TODO

> Implement regex input or a better way to help user select songs from the list instead of providing comma separated list.

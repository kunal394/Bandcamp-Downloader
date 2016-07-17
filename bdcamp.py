#!/usr/bin/env python

"""download url for any track will be of the form:
    https://p4.bcbits.com/download/track/f292a04c35c0d77096070e1a21ba2bd8/mp3-128/2174833463?fsig=c2438177b7ea6a2c2bbdc4a338c6f891&id=2174833463&stream=1&ts=1467921600.0&token=1467921660_41b8c540f50cd2cc51f629d1ae70bd94301999e3

    which is obtained from a url of type:
    https://popplers5.bandcamp.com/download/track?enc=mp3-128&fsig=66bf9341f2d63db3a4e203935b5a025c&id=2174833463&stream=1&ts=1465344506.0
     """

import signal, time, os, sys, requests, re, argparse
from bs4 import BeautifulSoup

verbose = False
automate = False
noconfirm = False

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

def vprint(arg):
    global verbose
    if verbose:
        for i in arg:
            print i

def parse_url(url):

    print """\n\nWarning!!! Either input a list of comma separated song nos
           to download particular songs or \"all\" to download the
           complete album. For example to download song nos 1, 2
           and 4, input 1, 2, 4"""
    print "Please adhere to the input format, otherwise the downloader won't behave as expected!!!\n\n"

    vprint(["Fetching data from the url provided..."])

    r = requests.get(url)

    vprint(["Data fetching complete", "Parsing data..."])

    s = BeautifulSoup(r.text, 'html.parser')

    vprint(["Parsing directory paths..."])

    dpath = []
    t = url.split('/')[3]
    
    vprint(["type: " + t])

    if t == 'track':
        vprint(['in track'])
        albumname = s.find("div", {"id" : "name-section"}).span.a.string.srtip().title()
        dpath.append(albumname)
        handle_track_album(s, dpath, {})
    elif t == 'album' or t == '' or t == "releases":
        vprint(['in album'])
        bandname = s.find("div", {"id" : "name-section"}).span.a.string.strip().title()
        dpath.append(bandname)
        albumname = s.find("div", {"id" : "name-section"}).h2.string.strip().title()
        dpath.append(albumname)
        handle_track_album(s, dpath, {})
    elif t == 'music':
        vprint(['in music'])
        bandname = s.find("span", {"class" : "title"}).string.title()
        dpath.append(bandname)
        albumlist = { i.string.strip() : i.parent.attrs['href'] for i in s.find_all("p", {"class" : "title"}) if i.string is not None }
        handle_artist(albumlist, url, dpath)

def handle_artist(albumlist, url, dpath):
    album_dict = {}
    for i in albumlist:
        album_url = url[::-1].partition('/')[2][::-1] + albumlist[i]

        vprint(["\nAlbum Name: " + i, "Fetching data from the album url: " + album_url + "... "])
        r = requests.get(album_url)
        vprint(["Data fetching complete", "Parsing data..."])
        s = BeautifulSoup(r.text, 'html.parser')

        vprint(["Fetching songs list for album: " + i + " from url: " + album_url])
        print "\nSelect songs for the album: " + i
        dl_dict = fetch_download_url(s, dpath)

        if len(dl_dict) is not 0:
            album_dict.update({i : dl_dict})

    if len(album_dict) == 0:
        print "No songs selected"
    else:
        print "List of the songs about to be downloaded:"
        for i in album_dict:
            print "\n\tAlbum Name: " + i
            for j in album_dict[i]:
                print "\t\tSong Name: " + album_dict[i][j][0]

        for i in album_dict:
            dpath.append(i)
            print "\nDownloading songs selected in the album: " + i
            handle_track_album(s.clear(), dpath, album_dict[i])
            print "Album " + i + " downloaded"
            dpath.remove(i)

def handle_track_album(s, dpath, dl_dict):
    if len(dl_dict) == 0:
        dl_dict = fetch_download_url(s, dpath)    

    if len(dl_dict) == 0:
        print "No songs selected"
    else:
        print "Creating the directory structure... "
        dirpath = "."
        for i in dpath:
            dirpath = dirpath + '/' + str(i)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        for i in dl_dict:
            print "Downloading " + str(i) + ': ' + dl_dict[i][0] + "... "
            download_song(dirpath + '/' + dl_dict[i][0] + '.mp3', dl_dict[i][1])
            print "Downloading Complete"

def fetch_download_url(s, dpath):
    global automate, noconfirm

    vprint(["Parsing songs list..."])

    #fetch all script tags inside body
    js = s.body.find_all("script")

    fetch_list = []
    #pattern to search for the urls along with title
    #[^\"] means anything other than "
    pattern=re.compile(ur'\"title\":\"[^\"]*\",\"file\":\{[^\}]*\}')

    #create list of the api calls needed to download songs
    for j in js:
        temp = pattern.findall(unicode(j))
        if len(temp) is not 0:
            fetch_list.extend(temp)

    vprint(["Songs list created", "Creating songs dictionary..."])

    songs_dict = {}
    #dictionary of songs with the api links
    for i, j in zip(range(1, len(fetch_list) + 1), fetch_list):
        title = j.split(':')[1].split(',')[0].split('"')[1]
        furl = "https:" + j.split(':')[3].split('}')[0].split('"')[1]
        songs_dict.update({i : [title, furl]})

    vprint(["Songs dictionary created", "Get the list of songs to download from user..."])

    if automate:
        dl_list = [s for s in songs_dict]
        print "List of songs to be downloaded:"
        for i in dl_list:
            if i in songs_dict:
                print str(i) + ': ' + songs_dict[i][0]
    elif noconfirm:
        dl_list = display_songs(songs_dict)
    else:
        dl_list = select_songs(songs_dict)

    vprint(["Download list received from user", "Creating dictionary of songs to download..."])

    dl_dict = {}
    #dictionary of songs with the download links
    for i in dl_list:
        title = songs_dict[i][0]
        furl = songs_dict[i][1]
        vprint(["Fetching download url for the song: " + title])
        dlurl = requests.get(furl, allow_redirects = False).headers['Location']
        dl_dict.update({i : [title, dlurl]})
    
    return dl_dict

def select_songs(songs_dict):

    user_response = 'n'
    while user_response.strip() is not 'y':
        dl_list = display_songs(songs_dict)    
        print "Are you sure you are done with your songs' choice and you want to go ahead and download them?"
        user_response = raw_input("y/n/c(to cancel): ")
        if user_response.strip() == 'c':
            print "Downloading canceled"
            sys.exit()
        while user_response.strip() is not 'y' and user_response.strip() is not 'n':
            print "Please enter a corect response!!"
            user_response = raw_input("y/n/c(to cancel): ")
            if user_response.strip() == 'c':
                print "Downloading canceled"
                sys.exit()
    return dl_list            

def display_songs(songs_dict):
    #print songs_dict
    for key in songs_dict:
        print str(key) + ": " + songs_dict[key][0]
    print ""    
    
    user_input = raw_input()
    if user_input.strip() == 'all':
        dl_list = [s for s in songs_dict]
    else:
        dl_list = [int(s) for s in user_input.split(',') if s.strip().isdigit()]
    
    dl_list = list(set(dl_list))

    print "\nYou have selected following songs:"
    for i in dl_list:
        if i in songs_dict:
            print str(i) + ': ' + songs_dict[i][0]
        else:
            dl_list.remove(i)
    if len(dl_list) == 0:
        print "Oops!! Looks like you either entered wrong song nos or none at all."

    return dl_list

def open_file(song_file):
    while True:
        try:
            f = open(song_file, 'wb')
        except IOError as e:
            print e.errno
            old_song_file = song_file
            print "Invalid song name: " + song_file + "."
            song_file = raw_input("Please provide a valid name along with the absolute path as present in the invalid name: ")
            print "Changing file name from " + old_song_file + " to " + song_file 
        else:
            return f

def download_song(song_file, url):

    f = open_file(song_file)

    print "Downloading " + song_file + "..."
    data = requests.get(url, stream = True)
    for chunk in data.iter_content(chunk_size=1024*1024):
        if chunk:
            print "len: " + str((len(chunk))/(1024*1024)) + "MB"
            f.write(chunk)
    f.close()
    return data        



#first download:https://oortcloudx.bandcamp.com/album/oort-cloud

if __name__ == "__main__":
    if (int(requests.__version__[0]) == 0):
        print ("Your version of requests needs updating\nTry: '(sudo) pip install -U requests'")
        sys.exit()

    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    #argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
    parser.add_argument("-n", "--noconfirm", help = "do not ask for confirmation", action = "store_true")
    parser.add_argument("-a", "--all", help = "download everything", action = "store_true")
    parser.add_argument("music_url", help = "Bandcamp Song URL")
    args = parser.parse_args()
    verbose = bool(args.verbose)
    noconfirm = bool(args.noconfirm)
    automate = bool(args.all)
    parse_url(args.music_url)

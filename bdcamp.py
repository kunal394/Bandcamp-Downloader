#!/usr/bin/env python

"""download url for any track will be of the form:
    https://p4.bcbits.com/download/track/f292a04c35c0d77096070e1a21ba2bd8/mp3-128/2174833463?fsig=c2438177b7ea6a2c2bbdc4a338c6f891&id=2174833463&stream=1&ts=1467921600.0&token=1467921660_41b8c540f50cd2cc51f629d1ae70bd94301999e3

    which is obtained from a url of type:
    https://popplers5.bandcamp.com/download/track?enc=mp3-128&fsig=66bf9341f2d63db3a4e203935b5a025c&id=2174833463&stream=1&ts=1465344506.0
    """

from main import *

verbose = False
automate = False
noconfirm = False

#verbose print
def vprint(arg):
    global verbose
    if verbose:
        for i in arg:
            print i

#verbose2 print
def vvprint(arg):
    global verbose2
    if verbose2:
        for i in arg:
            print i

#parse url to determine the type of download
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

    try:
        t = url.split('/')[3]
    except:
        #url is of the artist but does not ends with music
        t = 'music'
        url.strip('/')
        url += '/music'
    
    vprint(["type: " + t])

    if t == 'track':
        parse_track(s)

    elif t == 'album' or t == "releases":
        parse_album(s)

    elif t == 'music' or t == '':
        parse_artist(s, url)

def parse_track(s):
    vprint(['in track'])
    albumname = s.find("div", {"id" : "name-section"}).span.a.string.strip().title().replace('/', '-')
    dpath = [albumname]
    handle_track_album(s, dpath, {})

def parse_album(s):
    vprint(['in album'])
    try:
        bandname = s.find("div", {"id" : "name-section"}).span.a.string.strip().title().title().replace('/', '-')
        dpath = [bandname]
        albumname = s.find("div", {"id" : "name-section"}).h2.string.strip().title().replace('/', '-')
        dpath.append(albumname)
        vvprint(['Band-name: ' + bandname, 'Album-name: ' + albumname])
        handle_track_album(s, dpath, {})
    except:
        e = sys.exc_info()
        vprint(['Parsing as album failed!', str(e[0]) + ' ' + str(e[1])])

def parse_artist(s, url):
    vprint(['in music'])
    try:
        bandname = s.find("span", {"class" : "title"}).string.title()
        dpath = [bandname]
        albumlist = { i.string.strip().replace('/', '-').title() : i.parent.attrs['href'] for i in s.find_all("p", {"class" : "title"}) if i.string is not None }
        handle_artist(albumlist, url, dpath)
    except:
        e = sys.exc_info()
        vprint(['Parsing as artist failed!', str(e[0]) + ' ' + str(e[1]), 'Trying as album...'])
        parse_album(s)

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
        dl_dict = fetch_download_url(s)

        if len(dl_dict) is not 0:
            album_dict.update({i : dl_dict})

    display_artist(album_dict)

    for i in album_dict:
        dpath.append(i)
        print "\nDownloading songs selected in the album: " + i
        handle_track_album(s.clear(), dpath, album_dict[i])
        print "Album " + i + " downloaded"
        dpath.remove(i)

def display_artist(album_dict):
    if len(album_dict) == 0:
        print "No songs selected"
    else:
        print "List of the songs about to be downloaded:"
        for i in album_dict:
            print "\n\tAlbum Name: " + i
            for j in album_dict[i]:
                print "\t\tSong Name: " + album_dict[i][j][0]

def handle_track_album(s, dpath, dl_dict):
    if len(dl_dict) == 0:
        dl_dict = fetch_download_url(s)    

    if len(dl_dict) == 0:
        print "No songs selected"
    else:
        print "Creating the directory structure... "
        dirpath = "."
        for i in dpath:
            dirpath = dirpath + '/' + i

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        for i in dl_dict:
            print "Downloading " + str(i) + ': ' + dl_dict[i][0] + "... "
            download_song(dirpath + '/' + dl_dict[i][0] + '.mp3', dl_dict[i][1])

def fetch_download_url(s):
    global automate, noconfirm

    vprint(["Parsing songs list..."])

    #fetch all script tags inside body
    js = s.body.find_all("script")
    title_list = s.body.find_all('span', {'itemprop': 'name'})
    title_list = [i.text.replace('/', '-').title() for i in title_list]

    furl_list = []
    #pattern to search for the fetch urls
    #[^\"] means anything other than "
    furl_pattern=re.compile(ur'\/\/popplers[^\}]*\}')

    #create list of the api calls needed to download songs
    for j in js:
        temp = furl_pattern.findall(unicode(j))
        if len(temp) is not 0:
            furl_list.extend(temp)
    #remove the "} from the end of every furl
    furl_list = [i[:-2] for i in furl_list]
    vprint(["Songs list created", "Creating songs dictionary..."])
    vvprint(["Fetch list:", furl_list, "Title list:", title_list])
    if(len(furl_list) != len(title_list)):
        print("Error: title list and fetch list have different lengths")
        print("Title list:")
        print(title_list)
        print("Fetch list:")
        print(furl_list)
        sys.exit(1)

    songs_dict = {}
    #dictionary of songs with the api links
    for i in range(1, len(furl_list) + 1):
        songs_dict.update({i : [title_list[i - 1], 'https:' + furl_list[i - 1]]})

    vprint(["Songs dictionary created", "Get the list of songs to download from user..."])
    vvprint(["Songs dictionary:", songs_dict])

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
        vvprint(["Download url of " + title + ": " + dlurl])
        dl_dict.update({i : [title, dlurl]})
    
    return dl_dict

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
    parser.add_argument("-v", "--verbose", help = "increase output verbosity to level 1", action = "store_true")
    parser.add_argument("-vv", "--verbose2", help = "increase output verbosity to level 2", action = "store_true")
    parser.add_argument("-n", "--noconfirm", help = "do not ask for confirmation", action = "store_true")
    parser.add_argument("-a", "--all", help = "download everything", action = "store_true")
    parser.add_argument("music_url", help = "Bandcamp Song URL")
    args = parser.parse_args()
    verbose = bool(args.verbose)
    verbose2 = bool(args.verbose2)
    if verbose2:
        verbose = True
    noconfirm = bool(args.noconfirm)
    automate = bool(args.all)
    parse_url(args.music_url)

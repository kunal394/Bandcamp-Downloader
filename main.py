#!/usr/bin/env python

import signal, time, os, sys, requests, re, argparse
from bs4 import BeautifulSoup

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
    if user_input.strip().startswith('a'):
        dl_list = [s for s in songs_dict]
    else:
        dl_list = [int(s) for s in user_input.split(',') if s.strip().isdigit()]
    
    dl_list = list(set(dl_list))
    fdl_list = []
    
    print "\nYou have selected following songs:"
    for i in dl_list:
        if i in songs_dict:
            print str(i) + ': ' + songs_dict[i][0]
            fdl_list.append(i)
        else:
            print 'Removing Invalid Song No: ' + str(i)
    if len(fdl_list) == 0:
        print "Oops!! Looks like you either entered wrong song nos or none at all."

    return fdl_list

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
    
    #check if file exists
    if os.path.exists(song_file):
        down = check_info(song_file, url)
        if down is 0:
            print 'File already exists!!!'
            return 0
        else:
            #print 'Needs to be downloaded'
            #return 0
            f = open_file(song_file)
    else:
        f = open_file(song_file)

    print "Downloading " + song_file + "..."
    try:
        data = requests.get(url, stream = True)
        for chunk in data.iter_content(chunk_size=1024*1024):
            if chunk:
                print "len: " + str((len(chunk))/(1024*1024)) + "MB"
                f.write(chunk)
        f.close()
        print "Downloading Complete"
    except:
        e = sys.exc_info()
        os.unlink(f.name)
        print "Download Error: ", str(e[0]), str(e[1])
    #return data        

def check_info(song_file, url):
        data = requests.get(url, headers={'Range' : 'bytes=0-0'})
        if int(data.headers['Content-Range'].split('/')[1]) == os.path.getsize(song_file) :
            return 0
        else:
            return 1


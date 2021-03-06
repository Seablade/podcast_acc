'''
Copyright (C) August 2012  by Thomas Vecchione

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import ConfigParser, os, sys
import argparse
import logging
import logging.handlers
import youtube_upload
import ffmpeg_handler

from destinations import Destinations
from straight.plugin import load

from cgi import escape

presets = []

def readConfig (destination, config_file='settings.cfg'):
    '''
    Read the default configuration file
    '''
    tf = os.path.split(os.path.abspath(__file__))
    log.debug('Directory of this program: %s', tf[0])
    filename = tf[0] + '/../' + config_file
    log.debug('Using settings file: %s' % os.path.abspath(filename))
    log.debug('Script location: %s' % os.path.abspath(__file__))
    config = ConfigParser.ConfigParser()
    config.read(filename)
    presets = config.sections()
    for option in config.options(args.destination):
        setattr(destination, str(option), config.get(args.destination, str(option)))
        log.debug("Setting destination.%s to %s" % (str(option), config.get(args.destination, str(option))))

def uploadVideo (video, destination):
    '''
    This will start off the conversion process.  It will look up a destination
    and see what the appropriate format preset is for that destination.  It will
    will then convert the video into that format and upload the returned video file
    
    To start with it is only going to handle Youtube and Podcasts, but as things
    progress we will add destinations for Vimeo, etc. and add the ability to
    embed the appropriate destinations to Facebook, G+, Twitter, etc.
    
    This method should take the video file to upload, and the destination to
    upload it to and call the appropriate function
    '''
    pass

def find_Plugins(plugin, path="plugins", cls=Destinations):
    plugins = load(path, cls)
    for i in range(0,len(plugins)):
        log.debug("Plugin Found: %s", plugins[i].DESTINATION)
        if plugins[i].DESTINATION == plugin :
            log.debug("Destination %s found", plugins[i].DESTINATION)
            return plugins[i]
    
if __name__ == '__main__':
    log = logging.getLogger('PodcastLogger')
    log.setLevel(logging.DEBUG)

    handler = logging.handlers.SysLogHandler(address = ("/var/run/syslog"))

    log.addHandler(handler)

    ffmpeg = ffmpeg_handler.FFMPEG_Handler()
    parser = argparse.ArgumentParser(description="Podcast Management Software for Atlee Community Church")
    parser.add_argument("--format", choices=ffmpeg.readPresets(), help="The preset format to be used, if none is defined the file will be passed through as is instead of being converted.")
    parser.add_argument("--source", help="The source file to use for the podcast")
    parser.add_argument("--destination", help="The destination to upload the file to")
    parser.add_argument("--username", help="The username for the service if appropriate")
    parser.add_argument("--password", help="The password of the username if appropriate")
    parser.add_argument("--title", help="The title of the video")
    parser.add_argument("--description", help="A short description of the video")
    parser.add_argument("--category", help="Category to define the video")
    parser.add_argument("--playlist", help="A playlist to add the video to if appropriate")
    parser.add_argument("--type", help="Define the type of the destination")  # The type is for plugins like iTunes that might have multiple destinations
    args = parser.parse_args()
    
    path = str(os.path.dirname(os.path.realpath(__file__))) + "/plugins" # Add plugins directory to the system path
    sys.path.insert(0,path)
    print(sys.path)
    log.debug("Destination: %s" % str(args.destination))
    if args.type: # If there is a type specified on the commandline, use it, else look for a plugin named after the destination
        target = find_Plugins(plugin=args.type)
    else:
        target = find_Plugins(plugin=args.destination)
    destination = target()
    
    # Read Default Settings from Config File
    readConfig(destination) 
    
    # Now we override all the defaults with the commandline arguments
    if args.format:
        log.debug("Command Line Format: %s", args.format)
        destination.format=args.format
    if args.username:
        log.debug("Command Line Username: %s", args.username)
        destination.username=args.username
    if args.password:
        log.debug("Password provided on Commandline, not reprinted for security")
        destination.password=args.password
    if args.category:
        log.debug("Command Line Category: %s", args.category)
        destination.category=escape(args.category)
    if args.title:
        log.debug("Command Line Title: %s", args.title)
        destination.title=escape(args.title)
    if args.description:
        log.debug("Command Line Description: %s", args.description)
        destination.description=escape(args.description)
    if args.playlist:
        log.debug("Command Line Playlist: %s", args.playlist)
        destination.playlist=escape(args.playlist)
    if not args.source:
        print("A source file must be provided, exiting....")
        exit()
    else:
        log.debug("Command Line Source File: %s", str(args.source))
        destination.source=os.path.abspath(os.path.expanduser(args.source))


    '''
    If there is a preset defined, either in the config or on the commandline,
    then use ffmpeg to convert the file.  Otherwise pass through the file as is.

    TODO: Figure out why destination.format appears empty here.
    '''
    if args.format or (not destination.preset == ''):
        if args.format:
            video = ffmpeg.convertVideo(args.source, args.format)
        else:
            video = ffmpeg.convertVideo(args.source, destination.preset)
            log.debug('Destination format not empty, current value is: %s' % destination.format)
    else:
        log.debug('Destination format empty, current value is: %s  <-- Should be empty' % str(destination.format))
        video = str(args.source)
    
    destination.setup()
    destination.send(video)
    destination.teardown()

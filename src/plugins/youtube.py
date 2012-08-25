'''
Copyright (C) Aug 19, 2012  by seablade

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

from destinations import Destinations

# import os
# import re
# import sys
# import time
# import string
# import locale
# import urllib
# import socket
# import getpass
# import StringIO
# import optparse
# import itertools
# python >= 2.6
# from xml.etree import ElementTree

# python-gdata (>= 1.2.4)
import gdata.media
# import gdata.service
# import gdata.geo
# import gdata.youtube
import gdata.youtube.service
# from gdata.media import YOUTUBE_NAMESPACE
# from atom import ExtensionElement

try:
    import pycurl
except ImportError:
    pycurl = None
    
class InvalidCategory(Exception): pass
class VideoArgumentMissing(Exception): pass
class OptionsMissing(Exception): pass
class BadAuthentication(Exception): pass
class CaptchaRequired(Exception): pass
class ParseError(Exception): pass
class UnsuccessfulHTTPResponseCode(Exception): pass

EXIT_CODES = {
    # Non-retryable
    BadAuthentication: 1,
    VideoArgumentMissing: 2,
    OptionsMissing: 2,
    InvalidCategory: 3,
    CaptchaRequired: 4, # retry with options --captcha-token and --captcha-response
    ParseError: 5,
    # Retryable
    UnsuccessfulHTTPResponseCode: 100,
}


class Youtube(Destinations):
    '''
    classdocs
    '''
    VERSION = "0.7.1"
    DEVELOPER_KEY = "AI39si6kecyV82s7wseNZXLkl6gdVvr0LO7X3SKKCbmXtatQp95K-hnWbFlH3am2n3o7Hm_suXkvyJ0PH1UM3OYV00MWiwPXbA"
    DESTINATION = "Youtube"

    def __init__(self):
        '''
        Constructor
        '''
        self.name = 'Youtube'
        self.version = '0.1'
        service = gdata.youtube.service.YouTubeService()
        service.ssl = False
        service.developer_key = self.DEVELOPER_KEY
        service.source = 'my-example-application'
        self.service = service
        
        self.title = ''
        self.description = ''
        self.category = ''
        self.keywords = ''
        # self.source = ''
        self.format = ''
        self.username = ''
        self.password = ''
        self.playlist = ''
        
    def setup(self):
        """
        called before the plugin is asked to do anything
        
        In this case it sets up the login info etc.
        """
        self.service = gdata.youtube.service.YouTubeService()
        self.service.email = self.username
        self.service.password = self.password
        self.service.ProgrammaticLogin()
 
    def teardown(self):
        """called to allow the plugin to free anything"""
        pass
    
    def PrintEntryDetails(self, entry):
        print 'Video title: %s' % entry.media.title.text
        print 'Video published on: %s ' % entry.published.text
        print 'Video description: %s' % entry.media.description.text
        print 'Video category: %s' % entry.media.category[0].text
        print 'Video tags: %s' % entry.media.keywords.text
        print 'Video watch page: %s' % entry.media.player.url
        print 'Video flash player URL: %s' % entry.GetSwfUrl()
        print 'Video duration: %s' % entry.media.duration.seconds
        
        # non entry.media attributes
        '''
        These next three items don't seem to be working correctly, I don't
        really feel like going through and trying to figure out what they are
        supposed to be and fixing them, so for right now they will remain
        commented out.
        '''
        # print 'Video geo location: %s' % entry.geo.location()
        # print 'Video view count: %s' % entry.statistics.view_count
        # print 'Video rating: %s' % entry.rating.average
        
        # show alternate formats
        for alternate_format in entry.media.content:
            if 'isDefault' not in alternate_format.extension_attributes:
                print 'Alternate format: %s | url: %s ' % (alternate_format.type,
                                                         alternate_format.url)
        
        # show thumbnails
        for thumbnail in entry.media.thumbnail:
            print 'Thumbnail url: %s' % thumbnail.url

    def PrintVideoFeed(self, feed):
        for entry in feed.entry:
            self.PrintEntryDetails(entry)
 
    def createMetadata(self):
        pass
    
    def listVideos(self):
        uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % "default"
        self.PrintVideoFeed(self.service.GetYouTubeVideoFeed(uri))
 
    def checkStatus(self):
        upload_status = self.service.CheckUploadStatus(self.video)

        if upload_status is not None:
            video_upload_state = upload_status[0]
            detailed_message = upload_status[1]
 
    def send(self):
        """do whatever it is the plugin does"""
        # prepare a media group object to hold our video's meta-data
        self.media_group = gdata.media.Group(
          title=gdata.media.Title(text=self.title),
          description=gdata.media.Description(description_type='plain',
                                              text=self.description),
          keywords=gdata.media.Keywords(text=self.keywords),
          category=[gdata.media.Category(
              text=self.category,
              scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
              label=self.category)],
          player=None
        )
        
        # create the gdata.youtube.YouTubeVideoEntry to be uploaded
        video_entry = gdata.youtube.YouTubeVideoEntry(media=self.media_group)

        # Start the actual video upload hopefully...
        self.video = self.service.InsertVideoEntry(video_entry, self.source)

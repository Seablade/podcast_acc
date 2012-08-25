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

class Destinations(object):
    '''
    This is intended as an abstract style class for the use of defining new
    destinations via a plugin like API. It will define the basic structure that
    the program will call only, any plugin can obviously be much more complex.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.name = ''
        self.version = ''
        self.title = ''
        self.description = ''
        self.category = ''
        self.keywords = ''
        self.source = ''
        self.format = ''
        self.username = ''
        self.password = ''
        self.playlist = ''

    def setup(self, ffmpeg):
        """called before the plugin is asked to do anything"""
        raise NotImplementedError
 
    def teardown(self):
        """called to allow the plugin to free anything"""
        raise NotImplementedError
 
    def send(self):
        """do whatever it is the plugin does"""
        raise NotImplementedError
    

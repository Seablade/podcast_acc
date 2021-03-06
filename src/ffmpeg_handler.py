'''
Copyright (C) August 2012 by Thomas Vecchione

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

import ConfigParser, os
import logging as log
import subprocess

class FFMPEG_Handler(object):
    '''
    A class to handle video conversion via ffmpeg
    '''


    def __init__(self, preset_file='presets.cfg'):
        '''
        Constructor
        
        Set the config file
        '''
        self.config = ConfigParser.ConfigParser()
        self.passes = 0
        self.command = []
        self.output = ''
        self.extension = ''

        tf = os.path.split(os.path.abspath(__file__))
        log.debug('Directory of this program: %s', tf[0])
        filename = tf[0] + '/../' + preset_file
        log.debug('Using preset file: %s' % os.path.abspath(filename))
        log.debug('Script location: %s' % os.path.abspath(__file__))


        self.config.read(filename)
        log.debug("Using config file: " + str(os.path.abspath(filename)))
        return
    
    def readPresets (self):
        '''
        Read the defined ffmpeg presets from a file
        '''
        return self.config.sections() 
    
    def getOptions(self, preset, ffmpeg_pass=0):
        '''
        Get all items from the config file for a given preset, modify as
        needed and return the modified list
        '''
        options = []
        log.debug("Searching for items in preset: " + str(preset))
        items = self.config.items(preset)
        log.debug("Options are: " + str(items))
        log.debug("Option [0][0] = " + str(items[0][0]))
        self.filterPasses(items)
        log.debug("Options post return from setPasses(): " + str(items))
        if self.passes == 2:
            if ffmpeg_pass == 1:
                self.filterPass1(items)
            else:
                self.filterPass2(items)
        for item in items:
            if str(item[0]) == 'vn':
                print ('No Video Option found in the config file options')
                options.append('-vn')
            elif str(item[0]) == 'extension':
                print ('Extension found in the config file options: %s' % item[1])
                self.extension = str(item[1])
                print ('Extension assignment: %s' % self.extension)
            else:
                options.append("-" + str(item[0]))
                options.append(str(item[1]))
        log.debug("Options post adding - flag: " + str(options))
        return options

    def filterPasses(self, items):
        '''
        Remove the pass option as defined in the config file to be replaced
        later as appropriate otherwise we would always be doing the second pass
        of a two pass file on any preset that uses two passes
        '''
        for item in items:
            if item[0] == "pass":
                log.debug("pass item found")
                items.remove(item)
        # logging.debug("Options post pass removal: " + str(items))
        return
     
    def setPasses(self, preset):
        '''
        Set the passes member variable that is referenced when the command is
        built to determine if it is a single pass encoding or a two pass
        encoding
        '''
        items = self.config.items(preset)
        log.debug("self.passes == " + str(self.passes))
        for item in items:
            if item[0] == "pass":
                log.debug("pass item found")
                self.passes=item[1]
                log.debug("setPasses self.passes == " + str(self.passes))
                items.remove(item)
                break
            else:
                log.debug("Else clause fired")
                self.passes=1
        return
    
    def filterPass1(self, items):
        '''
        Remove all audio flags from the first pass of a two pass encoding as
        they aren't needed.  Also add in the flag to indicate the first pass of
        a two pass recording
        '''
        audioflags = ['acodec', 'ac', 'ab', 'ar'] # Define all possible audio options here
        for flag in audioflags:
            for item in items:
                if item[0] == flag:
                    items.remove(item)
        items.append(['pass', '1'])
        '''
        TODO: In actuality we should just be rendering to NULL, this requires
        different destinations on Windows vs *nix
        '''
        return
    
    def filterPass2(self, items):
        '''
        Add in appropriate flags for the second pass of the two pass recording
        '''
        items.append(['pass', '2'])
        return
    
    def checkDefaults(self):
        '''
        This is where overall program settings need to be handled.  In the
        config file they should go under the Defaults section.  Right now the
        only one that is handled is the threads command
        '''
        print("length of self.command: %d" % len(self.command))
        print("Contents of command[1]: %s" % str(self.command[0]))

        if self.config.has_option("Default", "threads"):
            for i in range(0,len(self.command)):
                print("Checking the contents of command[%d]: %s" % (i, self.command[i]))
                log.debug("i == " + str(i))
                self.command[i].insert(1, "-threads")
                self.command[i].insert(2, self.config.get("Default", "threads"))
        return

    def buildCommand(self, video, preset):
        '''
        Take the preset name and video file and build the full command from it
        '''
        self.setPasses(preset)
        log.debug("buildCommand self.passes == " + str(self.passes))
        if self.passes == 1:
            options = self.getOptions(preset)
            log.debug("options: %s" % str(options))
            print("Options: %s" % str(options))
            self.command.append(self.buildCommandString(video, options))
            self.checkDefaults()
            log.debug("The final command to be run (Single-Pass): " + str(self.command))
        else: # Assume that if passes != 1, it should be a two pass recording
            log.debug("buildCommand check completed succesfully")
            for i in range(1,3):
                # logging.debug("i == " + str(i))
                command = self.getOptions(preset, ffmpeg_pass=i)
                self.buildCommandString (video, command)
                if i == 1:
                    command.insert(len(command)-1, '-pass')
                    command.insert(len(command)-1, '1')
                    command.insert(1, '-y')
                    command.insert(len(command)-1, '-an')
                elif i == 2:
                    command.insert(len(command)-1, '-pass')
                    command.insert(len(command)-1, '2')
                    command.insert(1, '-y')
                self.command.append(command)
                self.checkDefaults()
            log.debug("The final command to be run (Two-Pass): " + str(self.command))
        return

    def buildCommandString(self, video, options):
        print('The current destination extension is: %s' % self.extension)
        if self.extension == '':
            print('self.extension has been found to be equal to \'\'')
            self.extension = os.path.splitext(video)[1]
        print('The current destination extension after the check is: %s' % self.extension)
        path = os.path.split(str(video))
        self.output = os.path.splitext(path[1])[0] + self.extension
        # command = options
        options.insert(0, str(video))
        options.insert(0, "-i")
        options.insert(0, "/usr/local/bin/ffmpeg")
        options.append("/tmp/" + str(self.output))
        return options


    def convertVideo (self, video, preset, tmp='/tmp'):
        '''
        This method should convert the video to a target format
        The format should be a preset as defined in the presets file
        The destination for the converted file will default to /tmp
          to ensure that it is removed on reboot and doesn't take up
          space it doesn't need to
        The method should return a pointer to the file, either a path
          or a file object, whatever is appropriate for Python
        '''

        
        self.buildCommand(video, preset)
        if len(self.command) > 1:
            if not subprocess.call(self.command[0]):
                print("Pass 1 completed succesfully, now running pass 2")
                log.debug("Pass 1 completed succesfully, now running pass 2")
                subprocess.call(self.command[1])
        else:
            print("Not a 2 Pass Recording, trying to convert")
            subprocess.call(self.command[0])
            log.debug("Completed the video file")
        hinted = str(os.path.splitext(self.output)[0]) + '-hinted' + str(os.path.splitext(self.output)[1])
        s = tmp + "/" + self.output
        d = tmp + "/" + hinted
        subprocess.call(['/usr/local/bin/qt-faststart', s, d])
        return d

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

'''
This code based in part off of some code I found here...
http://code.activestate.com/recipes/576810-copy-files-over-ssh-using-paramiko/

And a random reference for myself...
http://jessenoller.com/2009/02/05/ssh-programming-with-paramiko-completely-different/
'''

from destinations import Destinations

import os
import paramiko
import urllib
import xml.etree.ElementTree as ET
from time import gmtime, strftime

import logging as log


class Video(Destinations):
    '''
    This is a plugin to handle uploading to an iTunes style video podcast on a private server
    
    TODO: factor out the authentication code into it's own function so that we
    aren't duplicating code for the file upload and XML editing functions
    
    '''
    DESTINATION = 'Video'


    def __init__(self):
        '''
        Constructor
        '''
        self.name = 'Video'
        self.version = '0.1'
        self.title = ''
        self.description = ''
        self.category = ''
        self.keywords = ''
        self.source = ''
        self.format = ''
        self.username = ''
        self.password = ''
        self.playlist = ''
        self.key = ''
        self.host = ''
        self.xml = ''
        self.port = ''
        self.dir_remote = ''
        self.dir_local = ''
        self.port = 22
        self.link = ''
        self.author = ''


    def setup(self):
        """called before the plugin is asked to do anything"""
        pass
 
    def teardown(self):
        """called to allow the plugin to free anything"""
        pass

    def agent_auth(self, transport, username):
        """
        Attempt to authenticate to the given transport using any of the private
        keys available from an SSH agent or from a local private RSA key file (assumes no pass phrase).
        """

        # ki = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.expanduser(self.key)))
        ki = paramiko.RSAKey.from_private_key_file(os.path.abspath(os.path.expanduser(self.key)))

        '''
        try:
            log.debug("In Agent_Auth...")
            log.debug("self.key: %s" % os.path.abspath(os.path.expanduser(self.key)))
            log.debug("self.key: %s" % os.path.split(self.key)[1])
            ki = paramiko.RSAKey.from_private_key_file(os.path.split(self.key)[1])
            log.debug("Where the hell am I now?")    
        except Exception, e:
            print 'Failed loading' % (self.key, e)
        '''
        agent = paramiko.Agent()
        log.debug("Where the hell am I now?")
        agent_keys = agent.get_keys() + (ki,)
        if len(agent_keys) == 0:
            return
        log.debug("About to attempt all keys in agent_keys")
        for key in agent_keys:
            print ('Trying ssh-agent key %s' % str(key.get_fingerprint().encode('hex'),))
            try:
                transport.auth_publickey(username, key)
                print '... success!'
                return
            except paramiko.SSHException, e:
                print '... failed!', e
 
    def upload(self, local_file):
        '''
        This will transmit the file and update the XML.
        
        @file -- str path to filename
        
        TODO: Test File Transfer
        TODO: Add in ability to update XML
        '''
        hostkeytype = None
        hostkey = None
        files_copied = 0
        remote_file = os.path.join(self.dir_remote, os.path.split(local_file)[1])
                
        try:
            host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                # try ~/ssh/ too, e.g. on windows
                host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
            except IOError:
                print '*** Unable to open host keys file'
                host_keys = {}
        
        if host_keys.has_key(self.host):
            hostkeytype = host_keys[self.host].keys()[0]
            hostkey = host_keys[self.host][hostkeytype]
            print ('Using host key of type %s' % str(hostkeytype))
        
        # now, connect and use paramiko Transport to negotiate SSH2 across the connection
        try:
            print ('Establishing SSH connection to: %s:%d...' % (self.host,self.port))
            t = paramiko.Transport((self.host, self.port))
            t.start_client()
            
            log.debug("Agent Authentication proceeding...")
            self.agent_auth(t, self.username)
            log.debug("Agent Authentication Succeeded, continuing on...")
            if not t.is_authenticated():
                print ('RSA key auth failed! Trying password login...')
                t.connect(username=self.username, password=self.password, hostkey=hostkey)
            else:
                print ('Opening Session')
                sftp = t.open_session()
            sftp = paramiko.SFTPClient.from_transport(t)
        
            # dirlist on remote host
        #    dirlist = sftp.listdir('.')
        #    print "Dirlist:", dirlist
        
            try:
                sftp.mkdir(self.dir_remote)
            except IOError, e:
                print '(assuming ', self.dir_remote, 'exists)', e
        
            # TODO: Confirm and implement splicing the file name and path together
            print 'Copying', local_file, 'to ', remote_file
            sftp.put(local_file, remote_file)        
            t.close()
        
        except Exception, e:
            print ('*** Caught exception: %s: %s' % (e.__class__, e))
            try:
                t.close()
            except:
                pass
        print ('=' * 60)
        print ('Total files copied:',files_copied)
        print ('All operations complete!')
        print ('=' * 60)
 
    def addXMLEntry(self, xml, video):
        tree = ET.parse(xml)
        root = tree.getroot()
        i = 0
        
        while root[0][i].tag != 'item' : i+=1
        
        item = ET.Element('item')
        title = ET.SubElement(item, 'title')
        title.text = self.title
        link = ET.SubElement(item,'link')
        link.text = (self.link + os.path.split(video)[1])
        description = ET.SubElement(item, 'description')
        description.text = self.description
        guid = ET.SubElement(item, 'guid')
        guid.text = link.text
        author = ET.SubElement(item, 'author')
        author.text = self.author
        itunes_author = ET.SubElement(item, 'itunes:author')
        itunes_author.text = self.itunes_author
        pubdate = ET.SubElement(item, 'pubDate')
        pubdate.text = strftime("%a, %d %b %Y %H:%M:%S %z", gmtime())
        category = ET.SubElement(item, 'category')
        category.text = self.category
        stat = os.stat(video)
        filesize = stat.st_size
        enclosure = ET.SubElement(item, 'enclosure', {'length' : str(filesize) , 'type' : 'video/quicktime' , 'url' : str(link.text)})
        ET.dump(item)
        root[0].insert(i, item)
        
        log.debug('Inserting element: %s' % item.tag)
        log.debug('Current Item %s', root[0][i][0].text)
        
        local_file = '/tmp/' + self.xml
        ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        ET.ElementTree(root).write(local_file)
        return local_file

 
    def updateXML(self, video):
        tempxml = urllib.urlopen(self.link + self.xml)
        log.debug('Creating temporary xml file.')    
        local_file = self.addXMLEntry(tempxml, video)
        log.debug('Local XML File %s Created.' % local_file)
        self.upload(local_file)


 
    def send(self, video):
        self.upload(os.path.abspath(os.path.expanduser(video)))
        self.updateXML(video)
    

# ACC Podcast Manager

This is a program intended first and foremost to manage podcast upload and download for Atlee Community Church.  It can 
have several destinations and new ones are made simply by adding plugins to the plugins directory and adding an
appropriate section in the .cfg file.

## Dependencies

### Homebrew
This is an optional install and only for OS X, but makes everything else below this much easier to do.

### Python 2.7
On OS X with versions of python less than 2.7, you need to update to 2.7  The easiest way to do this is through Homebrew,
which after being installed you can use to build and install Python.  Note that you will need to adjust your own $PATH or
specify the version of python.  This needs to be complete before you can install any of the modules below.

### Python Modules
Before this can run, you need to make sure you install paramiko, straight.plugin and the GData API files.  The latter have
to be downloaded from Google, the former is probably easiest installed via pip as follows...

sudo easy_install pip
sudo pip install straight.plugin
sudo pip paramiko

### FFMPEG
This program uses ffmpeg for encoding, so it will need to be installed.  Again on OS X this is best done through Homebrew.
As of this writing (September 6 at about 4AM) you need to compile from the version control of ffmpeg for certain features to
work.  In homebrew this is also easy by appending --HEAD to the install command.

## Install

As of right now, you cannot install this program, it is written to be run from the source directory with the config files
located in the base directory of the project.  This will change, but that is why this is a pre-1.0 version at the moment.
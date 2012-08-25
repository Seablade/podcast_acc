# ACC Podcast Manager

This is a program intended first and foremost to manage podcast upload and download for Atlee Community Church.  It can 
have several destinations and new ones are made simply by adding plugins to the plugins directory and adding an
appropriate section in the .cfg file.

## Dependencies

Before this can run, you need to make sure you install paramiko, straight.plugin and the GData API files.  The latter have
to be downloaded from Google, the former is probably easiest installed via pip as follows...

sudo easy_install pip
sudo pip install straight.plugin
sudo pip paramiko
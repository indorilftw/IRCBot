IRCBot
======

A basic, customizable IRC Bot in Python

Includes functionality of copying messages from one IRC channel to another (filtering them if needed).


### Usage: 
Edit the "Bot Configuration" part inside IRCBot.py to your needs, then run from a terminal one of the following commands:

1. "python IRCBot.py"  
	(normal)

2. "python IRCBOT.py &"  
	(runs on background)

3. "nohup python IRCBOT.py &"  
	(runs on background and keeps running after shell is closed)


### Available commands:
$join < #channel > - Makes bot join < #channel >

$leave < #channel >- Makes bot leave < #channel >

$quit - Exits bot program

$echo < command > - Echoes < command >

$addadmin \< name1 > \< name 2> .. - Adds users to admin list

$remadmin \< name1 > \< name2 > .. - Removes users from admin list

$parrot \< name1 > \< name 2> ... - Adds users to copy list

$mute \< name1 > \< name 2> ... - Removes users from copy list

$activate - Activates copy mode

$deactivate - Deactivates copy mode

$help - Shows help message
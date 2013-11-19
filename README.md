IRCBot
======

A basic IRCBot, based on [apbot](http://sourceforge.net/projects/apbot/)

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
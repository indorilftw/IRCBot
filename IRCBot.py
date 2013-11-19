## Basic IRC bot Based on apbot (http://sourceforge.net/p/apbot)
## Added: Message copy functions
## Usage: "python IRCBot.py"  (normal)
##        "python IRCBOT.py &" (runs on background)
##        "nohup python IRCBOT.py &" (runs on background and keeps running after shell is closed)

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 19-11-2013

import socket
import time

###########################
##   Bot Configuration   ##
###########################
HOST = "nana.irc.gr" # Server to connect to
HOME_CHANNEL = "#sourcechannel" # The home channel for your bot
NEWCHANNEL = "#targetchannel"  # the copy location
NICK = "CopyCat" # Your bots nick
PORT = 6667 # Port (it is normally 6667)
SYMBOL = "$" #symbol eg. if set to # commands will be #echo.
blank = ""


###########################
##   Bot Functions       ##
###########################
def ping(msg):
	s.send("PONG :"+ msg +"\r\n")
def joinchan(channel):
	s.send("PRIVMSG "+ CHANNEL +" :Joining "+ channel +"\r\n")
	s.send("JOIN "+ channel +"\r\n")
def partchan(channel):
	s.send("PRIVMSG "+ CHANNEL +" :Leaving "+ channel +"\r\n")
	s.send("PART "+ channel +"\r\n")
def quitIRC():
	s.send("QUIT "+ CHANNEL +"\n")
def fail():
	s.send("PRIVMSG "+ CHANNEL +" :Either you do not have the permission to do that, or that is not a valid command.\n")
def echo(message):
	s.send("PRIVMSG "+ CHANNEL +" :"+ message +"\r\n") 

def copying(message):
	s.send("PRIVMSG " + NEWCHANNEL + " :" + message + "\r\n")

def main():
	#Connect to IRC Server and Channels
	s = socket.socket( )
	s.connect((HOST, PORT))
	s.send("USER "+ NICK +" "+ NICK +" "+ NICK +" :apbot\n")
	s.send("NICK "+ NICK +"\r\n")
	s.send("JOIN "+ HOME_CHANNEL +"\r\n")
	s.send("JOIN "+ NEWCHANNEL +"\r\n")

	#Bot Loop
	while True:
	  line = s.recv(2048)
	  line = line.strip("\r\n")
	  print line
	  stoperror = line.split(" ")
	  if ("PING :" in line): #Auto-respond to server pings
	        pingcmd = line.split(":", 1)
	        pingmsg = pingcmd[1]
	        ping(pingmsg)
	  elif "PRIVMSG" in line:
	      if len(line) < 30:
	        print blank
	      elif len(stoperror) < 4:
	        print blank
	      else:
	        complete = line.split(":", 2)
	        info = complete[1]
	        msg = line.split(":", 2)[2] ##the thing that was said
	        cmd = msg.split(" ")[0]
	        CHANNEL = info.split(" ")[2] ##channel from which it was said
	        user = line.split(":")[1].split("!")[0] ## the person that said the thing
	        arg = msg.split(" ")
	        
	        if CHANNEL == HOME_CHANNEL and user == "anon":
	          if (msg.split()[0][-1] != ":") or msg[0] == "!":
	            copying(msg)
	        elif SYMBOL + "join" == cmd and len(arg) > 1:
	          x = line.split(" ", 4)
	          newchannel = x[4]
	          joinchan(newchannel)
	        elif SYMBOL + "leave" == cmd and len(arg) > 1:
	          x = line.split(" ", 4)
	          newchannel = x[4]
	          partchan(newchannel)
	        elif SYMBOL + "quit" == cmd:
	          quitIRC()
	        elif SYMBOL + "echo" == cmd:
	          x = msg.split(" ", 1)[1]
	          echo(x)
	        elif SYMBOL in cmd:
	          fail()


if __name__ == '__main__':
	main()
## Basic Customizable IRC bot
## Added: Message copy functions
## Usage: "python IRCBot.py"  (normal)
##        "python IRCBOT.py &" (runs on background)
##        "nohup python IRCBOT.py &" (runs on background and keeps running after shell is closed)

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 19-11-2013

## TODO: SSL Connection

import socket
import time

###########################
##   Bot Configuration   ##
###########################
HOST = "nana.irc.gr"            # Server to connect to
HOME_CHANNEL = "#testchannel1"  # The home channel for your bot
COPY_CHANNEL = "#testchannel2"  # The copy location
NICK = "IRCBot"                 # Bot's nickname
PORT = 6667                     # Port to connect (usually 6667)
SYMBOL = "$"                    # Symbol eg. if set to # commands will be #echo.
master = "anon"                 # Owner
admins = [master]               # Admins list


###########################
##   Bot Functions       ##
###########################
def ping(msg):
    s.send("PONG :" + msg + "\r\n")
def joinchan(channel):
    s.send("PRIVMSG " + channel + " :Joining " + channel + "\r\n")
    s.send("JOIN "+ channel +"\r\n")
def partchan(channel):
    s.send("PRIVMSG " + channel + " :Leaving " + channel + "\r\n")
    s.send("PART " + channel + "\r\n")
def quitIRC():
    s.send("QUIT " + channel + "\n")
def fail():
    s.send("PRIVMSG " + channel + " :Either you do not have the permission to do that, or that is not a valid command.\n")
def echo(message):
    s.send("PRIVMSG " + channel + " :" + message + "\r\n") 

def copying(message):
    s.send("PRIVMSG " + COPY_CHANNEL + " :" + message + "\r\n")

def main():
    #Connect to IRC Server and Channels
    s = socket.socket( )
    s.connect((HOST, PORT))
    s.send("USER " + NICK + " " + NICK + " " + NICK + " :apbot\n")
    s.send("NICK " + NICK + "\r\n")
    s.send("JOIN " + HOME_CHANNEL +"\r\n")
    s.send("JOIN " + COPY_CHANNEL +"\r\n")

    #Bot Loop
    while True:
        line = s.recv(2048)
        line = line.strip("\r\n")
        print line
        stoperror = line.split(" ")
        if ("PING :" in line):                      # Auto-respond to server pings
            pingcmd = line.split(":", 1)
            pingmsg = pingcmd[1]
            ping(pingmsg)
        elif "PRIVMSG" in line:
            complete = line.split(":", 2)           # full message
            info = complete[1]
            msg = line.split(":", 2)[2]             # what was said
            cmd = msg.split(" ")[0]
            CHANNEL = info.split(" ")[2]            # channel from which it was said
            user = line.split(":")[1].split("!")[0] # the person that said it
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
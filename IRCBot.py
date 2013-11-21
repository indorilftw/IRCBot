#
## Basic Customizable IRC bot
## Added: Message copy functions
## Usage:   "python IRCBot.py"  (normal)
##          "python IRCBOT.py &" (runs on background)
##          "nohup python IRCBOT.py &" (runs on background and keeps running after shell is closed)

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 19-11-2013

## TODO: SSL Connection

import socket
from time import sleep
from sys import argv

###########################
##   Bot Configuration   ##
###########################
HOST = "nana.irc.gr"            # Server to connect to
HOME_CHANNEL = "#testchannel1"  # The home channel for your bot
COPY_CHANNEL = "#testchannel2"  # The copy location
NICK = "CopyBot"                # Bot's nickname
PORT = 6667                     # Port to connect (usually 6667)
SYMBOL = "$"                    # Symbol eg. if set to # commands will be #echo.
master = "anon"                 # Owner
s = socket.socket()             # Creates a socket
channel = ""                    # Original channel
copycat = True                  # Message copying
copyTarget = "Renelvon"         # Target to copy


###########################
##   Bot Functions       ##
###########################
def ping(msg):
    s.send("PONG :" + msg + "\r\n")

def joinchan(theChannel):
    s.send("PRIVMSG " + channel + " :Joining " + theChannel + "\r\n")
    s.send("JOIN "+ theChannel +"\r\n")

def partchan(theChannel):
    s.send("PRIVMSG " + channel + " :Leaving " + theChannel + "\r\n")
    s.send("PART " + theChannel + "\r\n")

def quitIRC():
    s.send("QUIT " + channel + "\n")

def fail():
    s.send("PRIVMSG " + channel + " :Invalid command. Send \"$help\" to show available commands \r\n")

def echo(message):
    print "\tPRIVMSG " + channel + " :" + message + "\r\n"
    s.send("PRIVMSG " + channel + " :" + message + "\r\n")

def copying(message):
    print "\tPRIVMSG " + COPY_CHANNEL + " :" + message + "\r\n"
    s.send("PRIVMSG " + COPY_CHANNEL + " :" + message + "\r\n")

def addadmin(currList, nicks):
    for name in nicks:
        if name not in currList:
            currList.append(name)
            print name + " added to admin list"
            s.send("PRIVMSG " + channel + " :" + name + " added to admin list\r\n")
        else:
            print name + " is already an admin"
            s.send("PRIVMSG " + channel + " :" + name + " is already an admin\r\n")
    return currList

def remadmin(currList, nicks):
    for name in nicks:
        if name in currList:
            if name != master:
                currList.remove(name)
                print name + " removed from admin list"
                s.send("PRIVMSG " + channel + " :" + name + " removed from admin list\r\n")
            else:
                print "Tried to remove master, failed."
                s.send("PRIVMSG " + channel + " :Cannot remove " + name + " from admins, he is my master\r\n")
        else:
            print name + " is not an admin"
            s.send("PRIVMSG " + channel + " :" + name + " is not an admin\r\n")
    return currList

def parrot(currList, nicks):
    for name in nicks:
        if name not in currList:
            currList.append(name)
            print name + " added to parrot list"
            s.send("PRIVMSG " + channel + " :" + name + " added to parrot list\r\n")
    return currList

def mute(currList, nicks):
    for name in nicks:
        if name in currList:
            currList.remove(name)
            print name + " removed from parrot list"
            s.send("PRIVMSG " + channel + " :" + name + " removed from parrot list\r\n")
    return currList


def main():
    #Connect to IRC Server and Channels
    s.connect((HOST, PORT))
    s.send("USER " + NICK + " " + NICK + " " + NICK + " :apbot\n")
    s.send("NICK " + NICK + "\r\n")
    s.send("JOIN " + HOME_CHANNEL +"\r\n")
    s.send("JOIN " + COPY_CHANNEL +"\r\n")
    
    admins = [master]       # Admins list
    active = copycat        # Copying activation based on config
    copyuser = [copyTarget] # List of users to copy

    #Bot Loop
    try:
        while True:
            line = s.recv(2048)
            lines = line.split("\r\n")
            for line in lines:                              # Magic: Assuming that only 1 line will be read, is WRONG
                print lines
                if ("PING :" in line):                      # Auto-respond to server pings
                    pingcmd = line.split(":", 1)
                    pingmsg = pingcmd[1]
                    ping(pingmsg)
                elif "PRIVMSG" in line:
                    complete = line.split(":", 2)           # Full message
                    info = complete[1]
                    msg = line.split(":", 2)[2]             # What was said
                    cmd = msg.split(" ")[0]
                    channel = info.split(" ")[2]            # Channel from which it was said
                    user = line.split(":")[1].split("!")[0] # The person that said it
                    arg = msg.split(" ")

                    if active == True and channel == HOME_CHANNEL and user in copyuser: # Copy messages
                        if (msg.split()[0][-1] != ":") or msg[0] == "!":
                            copying(msg)
                    if user in admins:
                        if SYMBOL + "join" == cmd and len(arg) > 1:                     # Join Channel
                            x = line.split(" ", 4)
                            newchannel = x[4]
                            joinchan(newchannel)
                        elif SYMBOL + "leave" == cmd and len(arg) > 1:                  # Leave Channel
                            x = line.split(" ", 4)
                            newchannel = x[4]
                            partchan(newchannel)
                        elif SYMBOL + "addadmin" == cmd and len(arg) > 1:               # Add admins
                            admins = addadmin(admins, arg[1:])
                        elif SYMBOL + "remadmin" == cmd and len(arg) > 1:               # Remove admins
                            admins = remadmin(admins, arg[1:])
                        elif SYMBOL + "parrot" == cmd and len(arg) > 1:                 # Add user to copy list
                            copyuser = parrot(copyuser, arg[1:])
                        elif SYMBOL + "mute" == cmd and len(arg) > 1:                   # Remove user from copy list
                            copyuser = mute(copyuser, arg[1:])
                        elif SYMBOL + "activate" == cmd:                                # Activate copying
                            active = True
                        elif SYMBOL + "deactivate" == cmd:                              # Deactivate copying
                            active = False
                        elif SYMBOL + "quit" == cmd:                                    # Quit Bot
                            quitIRC()
                        elif SYMBOL + "echo" == cmd:                                    # Echo command
                            x = msg.split(" ", 1)[1]
                            echo(x)
                        elif SYMBOL in cmd:                                             # Error
                            fail()
    except (KeyboardInterrupt, SystemExit):
        s.close()
        print "\n\nProgram Stopped. Exiting.."
    except Exception, e:
        s.close()
        print e
        print "\n\nProgram Stopped. Exiting.."


if __name__ == '__main__':
    main()
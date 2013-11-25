#
## Basic Customizable IRC bot
## Added: Message copy functions
## Usage:   "python IRCBot.py"  (normal)
##          "python IRCBOT.py &" (runs on background)
##          "nohup python IRCBOT.py &" (runs on background and keeps running after shell is closed)

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 25-11-2013

## TODO: SSL Connection, Flood protection (Threading), Fix Stubs, Dictionaries for plaisia

import socket
from time import sleep
from sys import argv

class IRCBot(object):
    def __init__(self):
        ###########################
        ##   Bot Configuration   ##
        ###########################
        self.HOST = "nana.irc.gr"               # Server to connect to
        self.HOME_CHANNEL = "#testchannel1"     # The home channel for your bot
        self.COPY_CHANNEL = "#testchannel2"     # The copy location
        self.NICK = "CopyBot"                   # Bot's nickname
        self.PORT = 6667                        # Port to connect (usually 6667)
        self.SYMBOL = "$"                       # Symbol eg. if set to # commands will be #echo.
        self.QUERY = "."                        # Symbol for bot queries
        self.master = "anon"                    # Owner (master account) of the bot
        ############################

        self.s = socket.socket()                # Creates a socket
        self.admins = [self.master]             # Admins list
        self.channel = ""                       # Message origin channel
        self.copyFlag = True                    # Message copying flag
        self.copyuser = ["Renelvon"]            # Target(s) to copy

        self.argCommands = {                    # Commands with arguments
            "join" : self.joinchan,
            "leave" : self.partchan,
            "addadmin" : self.addadmin,
            "remadmin" : self.remadmin,
            "parrot" : self.parrot,
            "mute" : self.mute,
            "echo" : self.echo,
        }


###########################
##   Bot Functions       ##
###########################

    def connect(self):
        #Connect to IRC Server and Channels
        self.s.connect((self.HOST, self.PORT))
        self.s.send("USER " + self.NICK + " " + self.NICK + " " + self.NICK + " :apbot\n")
        self.s.send("NICK " + self.NICK + "\r\n")
        self.s.send("JOIN " + self.HOME_CHANNEL +"\r\n")
        self.s.send("JOIN " + self.COPY_CHANNEL +"\r\n")

    def run(self):
        #Bot Loop
        while True:
            line = self.s.recv(2048)
            lines = line.split("\r\n")
            for line in lines:                              # Magic: Assuming that only 1 line will be read, is WRONG
                print line
                if ("PING :" in line):                      # Auto-respond to server pings
                    target = line.split(":", 1)[1]
                    self.pong(target)
                elif "PRIVMSG" in line:
                    msg = line.split(":", 2)[2]             # Message content
                    cmd = msg.split(" ")[0][1:]             # Command check
                    self.channel = line.split()[2]          # Channel from which it was said
                    user = line.split("!")[0][1:]           # The person that said it
                    arg = msg.split(" ")[1:]

                    if user in self.admins and msg[0] == self.SYMBOL:
                        if arg:
                            self.argCommands[cmd](arg)
                        elif "help" == cmd:                             # Show Help
                            self.showHelp(user)
                        elif "quit" == cmd:                             # Quit Bot
                            self.quitIRC()
                        elif "activate" == cmd:                         # Activate copying
                            self.copyFlag = True
                        elif "deactivate" == cmd:                       # Deactivate copying
                            self.copyFlag = False
                        else:                                           # Error
                            self.fail(user)

                    elif self.channel == self.HOME_CHANNEL:   # Message is on listening channel
                        if user in self.copyuser:
                            if msg[0] == self.QUERY:
                                #STUB
                                self.echo("Update")
                            elif self.copyFlag == True and msg.split()[0][-1] != ":":   # Copy messages
                                self.copying(msg)
                    elif msg[0] == self.QUERY:                                          # User Query
                        # FLOOD PROTECTION
                        echo("Query")


    def pong(self, msg):
        self.s.send("PONG :" + msg + "\r\n")

    def copying(self, message):
        print "\tPRIVMSG " + self.COPY_CHANNEL + " :" + message + "\r\n"
        self.s.send("PRIVMSG " + self.COPY_CHANNEL + " :" + message + "\r\n")

    def joinchan(self, channels):
        for ch in channels:
            self.s.send("PRIVMSG " + self.channel + " :Joining " + ch + "\r\n")
            self.s.send("JOIN "+ ch +"\r\n")

    def partchan(self, channels):
        for ch in channels:
            self.s.send("PRIVMSG " + self.channel + " :Leaving " + ch + "\r\n")
            self.s.send("PART " + ch + "\r\n")

    def addadmin(self, nicks):
        for name in nicks:
            if name not in self.admins:
                self.admins.append(name)
                print name + " added to admin list"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " added to admin list\r\n")
            else:
                print name + " is already an admin"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " is already an admin\r\n")

    def remadmin(self, nicks):
        for name in nicks:
            if name in self.admins:
                if name != self.master:
                    self.admins.remove(name)
                    print name + " removed from admin list"
                    self.s.send("PRIVMSG " + self.channel + " :" + name + " removed from admin list\r\n")
                else:
                    print "Tried to remove master, failed."
                    self.s.send("PRIVMSG " + self.channel + " :Cannot remove " + name + " from admins, he is my master\r\n")
            else:
                print name + " is not an admin"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " is not an admin\r\n")

    def parrot(self, nicks):
        for name in nicks:
            if name not in self.copyuser:
                self.copyuser.append(name)
                print name + " added to parrot list"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " added to parrot list\r\n")
            else:
                print name + " is already being repeated"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " is already being repeated\r\n")

    def mute(self, nicks):
        for name in nicks:
            if name in self.copyuser:
                self.copyuser.remove(name)
                print name + " removed from parrot list"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " removed from parrot list\r\n")
            else:
                print name + " is not being repeated"
                self.s.send("PRIVMSG " + self.channel + " :" + name + " is not being repeated\r\n")

    def showHelp(self, nick):
        self.s.send("PRIVMSG " + nick + " : $join < #channel > - Makes bot join < #channel >\r\n")
        self.s.send("PRIVMSG " + nick + " : $leave < #channel >- Makes bot leave < #channel >\r\n")
        self.s.send("PRIVMSG " + nick + " : $addadmin < name1 > < name2 > ... - Adds users to admin list\r\n")
        self.s.send("PRIVMSG " + nick + " : $parrot < name1 > < name2 > ... - Adds users to copy list\r\n")
        self.s.send("PRIVMSG " + nick + " : $mute < name1 > < name2 > ... - Removes users from copy list\r\n")
        self.s.send("PRIVMSG " + nick + " : $activate - Activates copy mode\r\n")
        self.s.send("PRIVMSG " + nick + " : $deactivate - Deactivates copy mode\r\n")
        self.s.send("PRIVMSG " + nick + " : $echo < command > - Echoes <command>\r\n")

    def quitIRC(self):
        self.s.send("QUIT " + self.HOME_CHANNEL + "\n")
        self.s.close()

    def fail(self, nick):
        self.s.send("PRIVMSG " + nick + " :Invalid command. Send \"$help\" to show available commands \r\n")

    def echo(self, args):
        message = " ".join(args)
        print "\tPRIVMSG " + self.channel + " :" + message + "\r\n"
        self.s.send("PRIVMSG " + self.channel + " :" + message + "\r\n")


def main():
    bot = IRCBot()
    try:
        bot.connect()
    except Exception, e:
        print e
        print "\n\nError Connecting. Exiting"
    try:
        bot.run()
    except (KeyboardInterrupt, SystemExit):
        print "\n\nProgram Stopped. Exiting.."
    except Exception, e:
        print e
        print "\n\nProgram Crashed. Exiting.."

if __name__ == '__main__':
    main()
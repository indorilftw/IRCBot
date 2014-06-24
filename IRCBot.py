## Basic Customizable IRC bot
## Usage:   "python IRCBot.py"  (normal)
##          "python IRCBOT.py &" (runs on background)
##          "nohup python IRCBOT.py &" (runs on background and keeps running after shell is closed)

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 17/06/2014

import ssl
import time
import socket
import threading
import ConfigParser
from sys import exit

# Modules to load
import modules.shmmy as shmmymod

class FloodThread (threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot

    def run(self):
      flag = True
      while True:
        self.bot.queried = set()
        self.bot.flood = set()
        print "Cleared flood entries"
        flag = not flag
        if flag:
          self.bot.warned = set()
          print "Cleared warning entries"
        time.sleep(300)



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
    self.sslSock = True
    ############################

    self.queried = set()                    # List of recent query users (1 query)
    self.flood = set()                      # Flood Protection list (2 queries)
    self.warned = set()                     # List of warned users (query after warning)
    self.blocked = set()                    # List of ignored users
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

  def setReplier(self, replier):
    self.replier = replier

###########################
##   Bot Functions       ##
###########################

  def connect(self):
    #Connect to IRC Server and Channels
    if self.sslSock:
      self.s = ssl.wrap_socket(self.s)
    self.s.connect((self.HOST, self.PORT))
    self.s.send("USER {0} {0} {0} :{0}\r\n".format(self.NICK))
    self.s.send("NICK {0} \r\n".format(self.NICK))
    if self.password:
      self.s.send("NICKSERV IDENTIFY {0} \r\n".format(self.password))
    self.s.send("JOIN {0} \r\n".format(self.HOME_CHANNEL))
    self.s.send("JOIN {0} \r\n".format(self.COPY_CHANNEL))

  def run(self):
    #Bot Loop
    while True:
      line = self.s.recv(2048)
      lines = line.split("\r\n")
      for line in lines:                          # Magic: Assuming that only 1 line will be read, is WRONG
        print line
        if "PING :" in line:                      # Auto-respond to server pings
          target = line.split(":", 1)[1]
          self.pong(target)
        elif "PRIVMSG" in line:
          msg = line.split(":", 2)[2]             # Message content
          cmd = msg.strip().split()[0][1:]        # Command check
          self.channel = line.split()[2]          # Channel from which it was said
          user = line.split("!")[0][1:]           # The person that said it
          arg = msg.strip().split()[1:]
          if user not in self.blocked:
            if user in self.admins and msg[0] == self.SYMBOL:
              if arg:
                try:
                  self.argCommands[cmd](arg)
                except KeyError:
                  print "KeyError on main program"
              elif "help" == cmd:                             # Show Help
                self.showHelp(user)
              elif "quit" == cmd:                             # Quit Bot
                self.quitIRC()
              elif "activate" == cmd:                         # Activate copying
                self.copyFlag = True
                self.s.send("PRIVMSG {0} : Copying activated\r\n".format(self.channel))
              elif "deactivate" == cmd:                       # Deactivate copying
                self.copyFlag = False
                self.s.send("PRIVMSG {0} : Copying deactivated\r\n".format(self.channel))
              else:                                           # Error
                self.fail(user)
            elif user in self.copyuser and self.channel == self.HOME_CHANNEL:   # Message is on listening channel
              if self.copyFlag == True:                                         # Copy messages, unless reply or command
                if msg.split()[0][-1] != ":" and msg[0] not in self.SYMBOL + self.QUERY:
                  self.copying(msg)
                elif msg[0] == self.QUERY:                                      # User Query
                  self.replier.decode(user, cmd, arg)
            elif self.channel != self.HOME_CHANNEL and msg[0] == self.QUERY:
              if user not in self.copyuser + self.admins :
                self.floodCheck(user)
              self.replier.decode(user, cmd, [])
            time.sleep(0.5)   # Flood protection

  def pong(self, msg):
    self.s.send("PONG :{0}\r\n".format(msg))

  def copying(self, msg):
    self.s.send("PRIVMSG {0} :{1} \r\n".format(self.COPY_CHANNEL, msg))

  def joinchan(self, channels):
    for ch in channels:
      self.s.send("PRIVMSG {0} :Joining {1} \r\n".format(self.channel, ch))
      self.s.send("JOIN {0} \r\n".format(ch))

  def partchan(self, channels):
    for ch in channels:
      self.s.send("PRIVMSG {0} :Leaving {1} \r\n".format(self.channel, ch))
      self.s.send("PART {0} \r\n".format(ch))

  def addadmin(self, nicks):
    for name in nicks:
      if name not in self.admins:
        self.admins.append(name)
        print "{0} added to admin list".format(name)
        self.s.send("PRIVMSG {0} :{1} added to admin list \r\n".format(self.channel, name))
      else:
        print "{0} is already an admin".format(name)
        self.s.send("PRIVMSG {0} :{1} is already an admin \r\n".format(self.channel, name))

  def remadmin(self, nicks):
    for name in nicks:
      if name in self.admins:
        if name != self.master:
          self.admins.remove(name)
          print "{0} removed from admin list".format(name)
          self.s.send("PRIVMSG {0} :{1} removed from admin list \r\n".format(self.channel, name))
        else:
          print "Tried to remove master, failed."
          self.s.send("PRIVMSG {0} :Cannot remove {1} from admins, he is my master \r\n".format(self.channel, name))
      else:
        print "{0} is not an admin".format(name)
        self.s.send("PRIVMSG {0} :{1} is not an admin \r\n")

  def parrot(self, nicks):
    for name in nicks:
      if name not in self.copyuser:
        self.copyuser.append(name)
        print "{0} added to parrot list".format(name)
        self.s.send("PRIVMSG {0} :{1} added to parrot list \r\n".format(self.channel, name))
      else:
        print "{0} is already being repeated".format(name)
        self.s.send("PRIVMSG {0} :{1} is already being repeated \r\n".format(self.channel, name))

  def mute(self, nicks):
    for name in nicks:
      if name in self.copyuser:
        self.copyuser.remove(name)
        print "{0} removed from parrot list".format(name)
        self.s.send("PRIVMSG {0} :{1} removed from parrot list \r\n".format(self.channel, name))
      else:
        print "{0} is not being repeated".format(name)
        self.s.send("PRIVMSG {0} :{1} is not being repeated \r\n".format(self.channel, name))

  def showHelp(self, nick):
    self.s.send("PRIVMSG {0} : $join < #channel > - Makes bot join < #channel > \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $leave < #channel > - Makes bot leave < #channel > \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $addadmin < name1 > < name2 > ... - Adds users to admin list \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $parrot < name1 > < name2 > ... - Adds users to copy list \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $mute < name1 > < name2 > ... - Removes users from copy list \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $activate - Activates copy mode \r\n".format(nick))
    self.s.send("PRIVMSG {0} : $deactivate - Deactivates copy mode\r\n".format(nick))
    self.s.send("PRIVMSG {0} : $echo < command > - Echoes <command>\r\n".format(nick))

  def quitIRC(self):
    self.s.send("QUIT {0} \r\n".format(self.HOME_CHANNEL))
    self.s.close()
    exit()

  def fail(self, nick):
    self.s.send("PRIVMSG {0} :Invalid command. Send \"$help\" to show available commands \r\n".format(nick))

  def echo(self, args):
    message = " ".join(args)
    self.s.send("PRIVMSG {0} :{1} \r\n".format(self.channel, message))

  def floodCheck(self, nick):
    if nick in self.warned:
      self.blocked.add(nick)
      self.s.send("PRIVMSG {0} : You ignored the flood warnings, you are now being ignored by the bot. \r\n".format(nick))
    elif nick in self.flood:
      self.warned.add(nick)
      self.s.send("PRIVMSG {0} : Warning: Do not attempt to flood the bot. Please wait 10 minutes before your next query. \r\n".format(nick))
    elif nick in self.queried:
      self.flood.add(nick)
      self.s.send("PRIVMSG {0} : Please wait 5 minutes before your next query. \r\n".format(nick))
    else:
      self.queried.add(nick)

  def config(self):
    config = ConfigParser.RawConfigParser()
    if config.read("bot.cfg"):  # Config file exists
      self.HOST = config.get('Configuration', 'HOST')
      self.HOME_CHANNEL = config.get('Configuration', 'HOME_CHANNEL')
      self.COPY_CHANNEL = config.get('Configuration', 'COPY_CHANNEL')
      self.NICK = config.get('Configuration', 'NICK')
      self.PORT = config.getint('Configuration', 'PORT')
      self.SYMBOL = config.get('Configuration', 'SYMBOL')
      self.QUERY = config.get('Configuration', 'QUERY')
      self.master = config.get('Configuration', 'master')
      self.password = config.get('Configuration', 'password')
      self.sslSock = config.getboolean('Configuration', 'SSL')
    else:
      print "Failed to locate configuration file"


def main():
  bot = IRCBot()
  bot.config()
  replier = shmmymod.Shmmy(bot)
  bot.setReplier(replier)
  mythread = FloodThread(bot)
  mythread.setDaemon(True)
  mythread.start()

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
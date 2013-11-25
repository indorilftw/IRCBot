# -*- coding: utf-8 -*-
## Extension module for shmmy IRC needs

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 25-11-2013

from time import strftime

class Shmmy(object):
  def __init__(self, bot):
    self.bot = bot
    self.plaisia = {}
    self.speaker = ""
    self.speakerTime = ""

    self.commands = {               # Module Commands
      "omilitis" : self.omilitis,
      "omilitis_" : self.setOmilitis,
      "clearOmilitis_" : self.clearOmilitis,
      "plaisia" : self.plaisia,
      "plaisia_" : self.setPlaisia,
      "clearPlaisia" : self.clearPlaisia,
      "help" : self.help,
      "help_" : self.help,
    }

  def decode(self, user, cmd, args):
    command = demux(cmd)
    try:
      if user in self.bot.copyuser:
        self.commands[command + "_"](user, args)
      else:
        self.commands[command](user)
    except KeyError:
      self.error(user)

  def demux(self, cmd):
    if cmd in ["ομιλιτης", "ομιλιτής", "speaker", "omilitis"]:
      return "omilitis"
    elif cmd in ["πλαισια", "πλαίσια", "plaisia"]:
      return "plaisia"
    elif cmd in ["απαρτια", "απαρτία", "apartia"]:
      return apartia
    else:
      return cmd


  def omilitis(self, nick):
    if self.speaker:
      self.bot.s.send("PRIVMSG {0} : Τρέχων ομιλιτής: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.speaker,self.speakerTime))
    else:
      self.bot.s.send("PRIVMSG {0} : Δεν έχει οριστεί ομιλιτής. \r\n".format(nick))

  def setOmilitis(self, nick, args):
    if args:
      self.speakerHistory.append((self.speaker,self.speakerTime))
      self.speaker = " ".join(args)
      self.speakerTime = strftime('%H:%M')
      self.bot.s.send("PRIVMSG {0} : Τρέχων ομιλιτής: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.speaker,self.speakerTime))
    else:
      self.omilitis(nick)

  def clearOmilitis(self, nick, args):
    self.omilitis = ""
    self.bot.s.send("PRIVMSG {0} : Δεν έχει οριστεί ομιλιτής. \r\n".format(nick))

  def plaisia(self, nick):
    if self.plaisia:
      for pl in self.plaisia:
        print pl, plaisia[pl]
    else:
      print "hi"

  def setPlaisia(self, nick, args):
    self.plaisia

  def clearPlaisia(self, nick, args):
    pass

  def help(self, nick, args=[]):
    pass

  def error(self, nick):
    pass
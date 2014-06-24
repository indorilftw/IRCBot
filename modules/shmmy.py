# -*- coding: utf-8 -*-
## Extension module for shmmy IRC needs

## Created By    : Vasilis Gerakaris <vgerak@gmail.com>
## Last Revision : 17/06/2014

from time import strftime, sleep
from os import makedirs
import errno
import datetime as dt

class Shmmy(object):
  def __init__(self, bot):
    self.bot = bot
    self.speaker = ""
    self.speakerTime = ""
    self.attendance = ""
    self.attendanceTime = ""
    self.createPath("logs")

    self.commands = {               # Module Commands
      "omilitis" : self.omilitis,
      "omilitis_" : self.setOmilitis,
      "clearOmilitis_" : self.clearOmilitis,
      "apartia" : self.apartia,
      "apartia_" : self.setApartia,
      "plaisia" : self.plaisia,
      "plaisia_" : self.setPlaisia,
      "order_" : self.order,
      "count_" : self.count,
      "undo_" : self.undo,
      "erase_last_" : self.undo,
      "clear_" : self.clear,
      "reset_" : self.clear,
      "results" : self.results,
      "results_" : self.results,
      "help" : self.help,
      "help_" : self.help,
    }

    self.counter = []
    self.plaisiaDict = {}

  def createPath(self, path):
      try:
          makedirs(path)
      except OSError as exception:
          if exception.errno != errno.EEXIST:
              raise

  def decode(self, user, cmd, args):
    command = self.demux(cmd)
    try:
      if user in self.bot.copyuser:
        self.commands[command + "_"](user, args)
      else:
        self.commands[command](user)
    except KeyError:
      self.error(user)
    except Exception, e:
      print e

  def demux(self, cmd):
    if cmd in ["ομιλητης", "ομιλητής", "speaker", "omilitis"]:
      return "omilitis"
    elif cmd in ["πλαισια", "πλαίσια", "plaisia"]:
      return "plaisia"
    elif cmd in ["απαρτια", "απαρτία", "apartia"]:
      return "apartia"
    elif cmd in ["αποτελεσματα", "αποτελέσματα", "results", "apotelesmata"]:
      return "results"
    else:
      return cmd

  def omilitis(self, nick):
    if self.speaker:
      self.bot.s.send("PRIVMSG {0} : Τρέχων ομιλητής: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.speaker,self.speakerTime))
    else:
      self.bot.s.send("PRIVMSG {0} : Δεν έχει οριστεί ομιλητής. \r\n".format(nick))

  def setOmilitis(self, nick, args):
    if args:
      self.speaker = " ".join(args)
      with open("logs/" + strftime("%d-%m-%Y_speakers.txt"), "a") as myfile:
        if self.speakerTime:
          prev = dt.datetime.strptime(self.speakerTime, '%H:%M')
          curr = dt.datetime.strptime(strftime('%H:%M'), '%H:%M')
          diff = (curr - prev).seconds
          myfile.write("Διάρκεια: {0:d} λεπτά\n\n".format(diff / 60))
        myfile.write("{0} - {1}\n".format(self.speaker, strftime('%H:%M')))
      self.speakerTime = strftime('%H:%M')
      self.bot.s.send("PRIVMSG {0} : Τρέχων ομιλητής: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.speaker,self.speakerTime))
    else:
      self.omilitis(nick)

  def clearOmilitis(self, nick, args):
    self.omilitis = ""
    self.bot.s.send("PRIVMSG {0} : Δεν έχει οριστεί ομιλητής. \r\n".format(nick))

  def apartia(self, nick):
    if self.attendance:
      self.bot.s.send("PRIVMSG {0} : Εκτιμώμενη απαρτία: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.attendance,self.attendanceTime))
    else:
      self.bot.s.send("PRIVMSG {0} : Δεν έχει δοθεί εκτίμηση για απαρτία. \r\n".format(nick))

  def setApartia(self, nick, args):
    if args:
      self.attendance = args[0]
      self.attendanceTime = strftime('%H:%M')
      self.bot.s.send("PRIVMSG {0} : Εκτιμώμενη απαρτία: {1}, Τελευταία ενημέρωση: {2} \r\n".format(nick,self.attendance,self.attendanceTime))
      with open("logs/" + strftime("%d-%m-%Y_attendance.txt"), "a") as myfile:
        myfile.write("{0} - Εκτιμώμενη απαρτία: {1}\n".format(self.attendanceTime, self.attendance))
    else:
      self.apartia(nick)

  def plaisia(self, nick):
    if self.plaisiaDict:
      for par in self.plaisiaDict:
        sleep(0.5)   # Flood protection
        self.bot.s.send("PRIVMSG {0} : {1} \r\n".format(nick, par.upper()))
        for pl in self.plaisiaDict[par]:
          self.bot.s.send("PRIVMSG {0} : --> {1} \r\n".format(nick, pl))
          sleep(1)   # Flood protection
    else:
      self.bot.s.send("PRIVMSG {0} : Δεν έχουν οριστεί πλαίσια. \r\n".format(nick))

  def setPlaisia(self, nick, args):
    if args:
      parataxi, plaisio = args[0], args[1:]
      if parataxi not in self.plaisiaDict:
        self.plaisiaDict[parataxi] = [" ".join(plaisio)]
      else:
        d[parataxi].append(" ".join(plaisio))
    else:
      self.plaisia(nick)

  def order(self, nick, args):
    if args:
      for i in args:
        self.counter.append([i,0])

  def results(self, nick, args=[]):
    if self.counter:
      print "Τρέχοντα αποτελέσματα"
      self.bot.s.send("PRIVMSG {0} : Τρέχοντα αποτελέσματα\r\n".format(nick))
      for i in sorted(self.counter, key=lambda x : x[1], reverse=True):
        print "{0:4} : {1}".format(i[1], i[0])
        self.bot.s.send("PRIVMSG {0} : {1:4} : {2}\r\n".format(nick, i[1], i[0]))
        sleep(0.5)  # Flood protection
    else:
      self.bot.s.send("PRIVMSG {0} : Δεν υπάρχουν ακόμη αποτελέσματα.\r\n".format(nick))

  def count(self, nick, args):
    if len(args[1:]) == len(self.counter):
      self.lastCount = args
      for i, val in enumerate(args[1:]):
        self.counter[i][1] += int(val)
      self.results(self.bot.HOME_CHANNEL)
    else:
      self.bot.s.send("PRIVMSG {0} : Λάθος αριθμός ορισμάτων\r\n".format(self.bot.HOME_CHANNEL))

  def undo(self, nick, args):
    for i, val in enumerate(self.lastCount):
      self.counter[i][1] -= int(val)
    self.results(self.bot.HOME_CHANNEL)

  def clear(self, nick, args):
    for i in self.counter:
        self.counter[i][1] = 0

  def help(self, nick, args=[]):
    self.bot.s.send("PRIVMSG {0} : Διαθέσιμες εντολές: .omilitis, .apartia, .apotelesmata, .plaisia \r\n".format(nick))
    if nick in self.bot.copyuser:
      self.bot.s.send("PRIVMSG {0} : Επιπλέον εντολές: .clearOmilitis, .order, .count, .undo, .clear \r\n".format(nick))

  def error(self, nick, args=[]):
    self.bot.s.send("PRIVMSG {0} : Η εντολή δεν υπάρχει. \r\n".format(nick))
    self.help(nick)

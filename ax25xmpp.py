#!/usr/bin/python -W ignore::DeprecationWarning

#
# Copyright (c) 2010 John Goerzen
#
# Based on xtalk.py from xmppy, Copyright 2003-2008 Alexey Nezhdanov
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this package; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
#   02110-1301, USA.


import sys,os,xmpp,time,select,fcntl
import xmpp.debug

EOL = "\r"

class Bot:

    def __init__(self,jabber,remotejid,presence):
        self.jabber = jabber
        self.remotejid = remotejid
        self.presencestr = presence
        self.hasresponded = False

    def register_handlers(self):
        self.jabber.RegisterHandler('message',self.xmpp_message)
        self.jabber.RegisterHandler('presence',self.xmpp_presence)

    def xmpp_message(self, con, event):
        type = event.getType()
        fromjid = event.getFrom().getStripped()
        if type in ['message', 'chat', None] and fromjid == self.remotejid:
            if event.getBody() == '!EX':
                sys.stdout.write("Connection closed by sysop." + EOL)
                sys.stdout.flush()
                sys.exit(0)
            if not self.hasresponded:
                #sys.stdout.write("Sysop has responded." + EOL)
                #sys.stdout.flush()
                self.hasresponded = True
            writebuf = ">>> " + event.getBody() + " <<<" + EOL
            while writebuf != "":
                sys.stdout.write(writebuf[0:60])
                sys.stdout.flush()
                writebuf = writebuf[60:]

    def stdio_message(self, message):
        m = xmpp.protocol.Message(to=self.remotejid,body=message,typ='chat')
        self.jabber.send(m)
        pass

    def xmpp_connect(self):
        con=self.jabber.connect()
        if not con:
            sys.stderr.write('could not connect!' + EOL)
            sys.stdout.flush()
            return False
        #sys.stdout.write("Paging sysop." + EOL)
        #sys.stdout.flush()
        #sys.stderr.write('connected with %s\n'%con)
        auth=self.jabber.auth(jid.getNode(),jidparams['password'],resource=jid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!' + EOL)
            sys.stdout.flush()
            return False
        #sys.stderr.write('authenticated using %s\n'%auth)
        self.register_handlers()
        return con

    def xmpp_presence(self, conn, presence_node):
        #print presence_node
        if presence_node.getFrom().bareMatch(self.remotejid):
            if presence_node.getType() == 'subscribe':
                replypres=xmpp.Presence(typ='subscribed',to=presence_node.getFrom())
                conn.send(replypres)
                replypres.setType('subscribe')
                conn.send(replypres)
            elif presence_node.getType() == 'probe':
                replypres = xmpp.Presence(to=presence_node.getFrom(),
                                          show='chat', status=self.presencestr)
                conn.send(replypres)
            elif ((not presence_node.getShow() is None) and  \
                  presence_node.getShow != '') :
                pass
                #sys.stdout.write("*** Status: " + presence_node.getShow() + "\n")

if __name__ == '__main__':

    if sys.stdin.isatty():
        EOL = "\n"
    if len(sys.argv) < 6:
        print "Syntax: ax25xmpp configfile JID port callwithssid nodenamewithssid [UNIXEOL]"
        sys.stdout.flush()
        sys.exit(0)

    logf = open("/tmp/ax25xmpp.log", "at")
    os.dup2(logf.fileno(), 2)
    configfile=sys.argv[1]
    tojid=sys.argv[2]
    incomingport=sys.argv[3]
    incomingcall=sys.argv[4]
    incomingnodename=sys.argv[5]
    if len(sys.argv) == 7 and sys.argv[6] == 'UNIXEOL':
        EOL = "\n"

    #sys.stdout.write("ax25xmpp bridge (c) 2010 John Goerzen, 2003-2008 Alexey Nezhdanov" + EOL)
    #sys.stdout.flush()
    sys.stdout.write("ax25xmpp bridge. Paging sysop. Type !EX to exit." + EOL)
    sys.stdout.flush()
    
    greeting1 = 'Chat request on port %s from call %s on node %s.  Type !EX to close session.' \
        % (incomingport, incomingcall, incomingnodename)
    presence = 'Bridged to port %s, call %s' % (incomingport, incomingcall)
    
    jidparams={}
    if os.access(configfile,os.R_OK):
        for ln in open(configfile).readlines():
            if not ln[0] in ('#',';'):
                key,val=ln.strip().split('=',1)
                jidparams[key.lower()]=val
    for mandatory in ['jid','password']:
        if mandatory not in jidparams.keys():
            open(configfile,'w').write('#Uncomment fields before use and type in correct credentials.\n#JID=romeo@montague.net/resource (/resource is optional)\n#PASSWORD=juliet\n')
            print 'Please point %s config file to valid JID for sending messages.' % configfile
            sys.stdout.flush()
            sys.exit(5)

    jid=xmpp.protocol.JID(jidparams['jid'])
    cl=xmpp.Client(jid.getDomain(),debug=["dispatcher"])
    
    bot=Bot(cl,tojid,presence)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!" + EOL)
        sys.stdout.flush()
        sys.exit(1)

    cl.sendInitPresence(requestRoster=1)   # you may need to uncomment this for old server
    pres = xmpp.Presence(show='chat', status=presence)
    cl.send(pres)
    bot.stdio_message(greeting1)
    
    socketlist = {cl.Connection._sock:'xmpp',sys.stdin:'stdio'}
    online = 1

    # Set to non-blocking

    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    readbuf = ""


    while online:
        (i , o, e) = select.select(socketlist.keys(),[],[],1)
        for each in i:
            if socketlist[each] == 'xmpp':
                cl.Process(1)
            elif socketlist[each] == 'stdio':
                msg = sys.stdin.read(4096)
                readbuf += msg

                # Process the buffer.
                splitted = readbuf.split(EOL)
                if len(splitted) > 1:
                    # we have 1 or more items to output
                    for item in splitted[:-1]:
                        if item == '!EX':
                            bot.stdio_message("Connection closed via !EX command from user")
                            sys.stdout.write("Connection closed at your request." + EOL)
                            sys.stdout.flush()
                            sys.exit(0)
                        bot.stdio_message(item)
                    # Put remainder back into buffer
                    readbuf = splitted[-1]
            else:
                raise Exception("Unknown socket type: %s" % repr(socketlist[each]))
    #cl.disconnect()

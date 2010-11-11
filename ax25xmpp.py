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


import sys,os,xmpp,time,select

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
                sys.stdout.write("Connection closed.\r\n")
                sys.exit(0)
            if not self.hasresponded:
                sys.stdout.write("Sysop has responded.\r\n")
                self.hasresponded = True
            sys.stdout.write(event.getBody() + '\r\n')

    def stdio_message(self, message):
        m = xmpp.protocol.Message(to=self.remotejid,body=message,typ='chat')
        self.jabber.send(m)
        pass

    def xmpp_connect(self):
        con=self.jabber.connect()
        if not con:
            sys.stderr.write('could not connect!\r\n')
            return False
        sys.stdout.write("Paging sysop.\r\n")
        #sys.stderr.write('connected with %s\n'%con)
        auth=self.jabber.auth(jid.getNode(),jidparams['password'],resource=jid.getResource())
        if not auth:
            sys.stderr.write('could not authenticate!\n')
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

    if len(sys.argv) < 5:
        print "Syntax: xtalk configfile JID port callwithssid nodenamewithssid"
        sys.exit(0)

    sys.stdout.write("ax25xmpp bridge (c) 2010 John Goerzen, 2003-2008 Alexey Nezhdanov\r\n")
    sys.stdout.write("bridge ready.\r\n")
    
    configfile=sys.argv[1]
    tojid=sys.argv[2]
    incomingport=sys.argv[3]
    incomingcall=sys.argv[4]
    incomingnodename=sys.argv[5]

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
            sys.exit(5)
    
    jid=xmpp.protocol.JID(jidparams['jid'])
    cl=xmpp.Client(jid.getDomain(),debug=[])
    
    bot=Bot(cl,tojid,presence)

    if not bot.xmpp_connect():
        sys.stderr.write("Could not connect to server, or password mismatch!\r\n")
        sys.exit(1)

    cl.sendInitPresence(requestRoster=1)   # you may need to uncomment this for old server
    pres = xmpp.Presence(show='chat', status=presence)
    cl.send(pres)
    bot.stdio_message(greeting1)
    
    socketlist = {cl.Connection._sock:'xmpp',sys.stdin:'stdio'}
    online = 1

    while online:
        (i , o, e) = select.select(socketlist.keys(),[],[],1)
        for each in i:
            if socketlist[each] == 'xmpp':
                cl.Process(1)
            elif socketlist[each] == 'stdio':
                msg = sys.stdin.readline().rstrip('\r\n')
                bot.stdio_message(msg)
            else:
                raise Exception("Unknown socket type: %s" % repr(socketlist[each]))
    #cl.disconnect()

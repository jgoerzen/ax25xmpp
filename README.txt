Welcome to the AX.25 <-> XMPP (Jabber) gateway.

Features
--------

 * Bidirectional chat bridge between AX.25 and Jabber.

 * Integrates with Jabber presence system.  Sets its state description
   to a dscription of the node that you're chatting with.  Indicates
   it's offline when the remote end drops the link.

 * Accepts details on the command line which are then passed to the
   Jabber user at the beginning of the chat.

 * Visually similar to ttylinkd for AX.25 users.

Installation
------------

You will need Python and the xmpppy package.  Debian users can get it
with apt-get install python-xmpp.  Others can find it at
http://xmpppy.sourceforge.net/.

Configuration
-------------

Create a config file somewhere.  It needs only two lines, which should
look like this:

JID=username@example.com
PASSWORD=foobar

You can optionally append a /resource to the JID if you wish.  This
configuration file gives the account that the bridge logs in to; the
command line gives the account it will transmit its messages to

Invocation
----------

You can run ax25xmpp from the shell for testing.  It will attempt to
auto-detect whether to use Unix \n line-endings or AX.25 \r
line-endings.  If it is called from a terminal, it uses \n endings.

The parameters are:

ax25xmpp /path/to/configfile destJID port call nodename [UNIXEOL]

port, call, and nodename are used for display purposes only.  You can
make them up if desired.  If you give UNIXEOL at the end, it will
force it to Unix line endings (as, for instance, called by the node
program).

Example Configuration
---------------------

an ax25d.conf line could be:

default 7 * * * * * -           nobody /usr/local/bin/ax25xmpp.py /usr/local/bin/ax25xmpp.py /etc/ax25/ax25xmpp.conf jgoerzen@example.com %d %S %R

And a node.conf line could be:

ExtCmd          CHat    1       nobody  /usr/local/bin/ax25xmpp.py /usr/local/bin/ax25xmpp.py /etc/ax25/ax25xmpp.conf jgoerzen@example.com node %S %R UNIXEOL

Example Session
---------------

Here is a typescript of an example session.

ax25xmpp bridge (c) 2010 John Goerzen, 2003-2008 Alexey Nezhdanov
Bridge ready.  Type !EX to close session.
Paging sysop.
Sysop has responded.
>>> good evening <<<
good evening to you, sysop.  having fun with chat?
>>> yes, lots of fun. <<<
bye
!EX
Connection closed at your request.

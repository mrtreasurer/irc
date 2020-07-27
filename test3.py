import socket

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "192.168.178.53"
channel = "#test"
botnick = "pythontest"
adminname = "Bert"
exitcode = "bye"

def joinchan(chan): # join channel(s).
  ircsock.send(bytes(f"JOIN {chan}\n", "UTF-8")) 
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1:  
    ircmsg = ircsock.recv(2048).decode("UTF-8")
##    ircmsg = ircmsg.strip('\r\n')
    print(ircmsg, end="")

def ping(): # respond to server Pings.
  ircsock.send(bytes("PONG :", "UTF-8"))

def sendmsg(msg, target=channel): # sends messages to the target.
  ircsock.send(bytes(f"PRIVMSG {target}: {msg}\n", "UTF-8"))

ircsock.connect((server, 6667))
ircsock.send(bytes(f"USER {botnick} {botnick} {botnick} {botnick}\n", "UTF-8"))
ircsock.send(bytes(f"NICK {botnick}\n", "UTF-8"))

joinchan(channel)

while True:
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\r\n')
    print(ircmsg)

    if ircmsg.find("PRIVMSG") != -1:
        name = ircmsg.split('!',1)[0][1:]
        message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

        if len(name) < 17:
            if message.find(f"Hi {botnick}") != -1:
                sendmsg(f"Hello {name}!")

            if message[:5].find('.tell') != -1:
                target = message.split(' ', 1)[1]

                if target.find(' ') != -1:
                    message = target.split(' ', 1)[1]
                    target = target.split(' ')[0]

                else:
                    target = name
                    message = "Could not parse. The message should be in the format of ‘.tell [target] [message]’ to work properly."

                sendmsg(message, target)

            if name.lower() == adminname.lower() and message.rstrip() == exitcode:
                sendmsg("oh...okay. :'(")
                ircsock.send(bytes("QUIT n", "UTF-8"))
                break

    else:
        if ircmsg.find("PING :") != -1:
            ping()
                

import queue
import socket


class IRC:
    def __init__(self, port, server, channel, botnick, textqueue, commandqueue):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.port = port
        self.server = server
        self.channel = channel
        self.botnick = botnick

        self.commandqueue = commandqueue
        self.textqueue = textqueue

        self.connected = False
        self.joined = False
        self.shutdown = False

    def connect(self):
        self.sock.connect((self.server, self.port))
        self.sock.send(bytes(f"USER {self.botnick} {self.botnick} {self.botnick} {self.botnick}\n", "UTF-8"))
        self.sock.send(bytes(f"NICK {self.botnick}\n", "UTF-8"))

        self.connected = True

    def join_channel(self):
        self.sock.send(bytes(f"JOIN {self.channel}\n", "UTF-8")) 
        msg = ""
        
        while msg.find("End of /NAMES list.") == -1:  
            msg = self.sock.recv(2048).decode("UTF-8")
            self.textqueue.put(msg)

        self.joined = True

    def sendmsg(self, msg, q=True): # sends messages to the target.
        self.sock.send(bytes(f"PRIVMSG {self.channel} {msg}\n", "UTF-8"))        
        self.textqueue.put(f"<{self.botnick}> {msg}\r\n")

    def ping(self):
        self.sock.send(bytes("PONG", "UTF-8"))

    def prettify(self, msg):
        return f"<{msg.split('!')[0][1::]}> {msg.split(':')[-1]}"

    def process(self):
        print("processing")
        while not self.shutdown:
            try:
                self.shutdown = self.commandqueue.get_nowait()

            except queue.Empty:
                pass

            if not self.shutdown:
                msg = self.sock.recv(2048).decode("UTF-8")

                if msg.find("PRIVMSG") != -1:
                    fmsg = self.prettify(msg)
                    self.textqueue.put(fmsg)

                else:
                    if msg.find("PING") != -1:
                        self.ping()
                        print("ponged")

        print("Shut down")


if __name__ == "__main__":
    import conf

    text = queue.Queue()
    command = queue.Queue()

    irc = IRC(conf.port, conf.server, conf.channel, conf.botnick, text, command)
    irc.connect()
    irc.join_channel()
    irc.sendmsg("hi")


import queue
import threading
import time
import tkinter as tk

import conf
from irc import IRC


class GUI(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master)

        self.master = master

        self.commandqueue = queue.Queue()
        self.textqueue = queue.Queue()

        self.irc = IRC(conf.port, conf.server, conf.channel, conf.botnick, self.textqueue, self.commandqueue)

        self.textbox = tk.Text(master=self)
        self.textbox.pack(fill=tk.BOTH, expand=1)

        self.entry = tk.Entry(master=self)
        self.entry.pack(fill=tk.X)

        self.joining = False
        self.processing = False
        self.shutdown = False

        connect = threading.Thread(target=self.irc.connect)
        connect.start()

        self.master.protocol("WM_DELETE_WINDOW", self.terminate)
        self.master.bind("<Return>", self.send)
        
        self.master.after(100, self.process)

    def run(self):
        self.master.mainloop()

    def process(self):
        if self.irc.connected:
            if self.irc.joined and not self.processing:
                self.processing = True
                process = threading.Thread(target=self.irc.process)
                process.start()
            
            elif not self.irc.joined and not self.joining:
                self.joining = True
                join = threading.Thread(target=self.irc.join_channel)
                join.start()
        
        try:
            msg = self.textqueue.get_nowait()

            self.textbox.insert(tk.END, msg)
            self.textbox.see(tk.END)

        except queue.Empty:
            pass

        if not self.shutdown:        
            self.master.after(100, self.process)

        else:
            print("Done")

    def send(self, *args):
        msg = self.entry.get()
        self.irc.sendmsg(msg)

        self.entry.delete(0, tk.END)

    def terminate(self):
        self.commandqueue.put(True)
        self.shutdown = True

        self.master.after(200, self.master.destroy)


if __name__ == "__main__":
    root = tk.Tk()

    test_frame = GUI(root)
    test_frame.pack(fill=tk.BOTH, expand=1)

    test_frame.run()
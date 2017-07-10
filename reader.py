#!/usr/bin/env python3

'''
do not use wildcard imports (ie `from module import *`)
use classes and subclasses for GUI elements
never use more than one call to Tk() in a program; all secondary windows need to use `Toplevel`
use descriptive variable names, and never use single-character variable names
never nest functions unless you are making a closure, and even then it's usually better to use functools.partial
Your program needs to layout using `pack`, you gain nothing from using `grid`.
If you do use `grid`, remember that if there is nothing in a row or column, it defaults to a width of 0. So there is no point to skipping row or column numbers.
hard coded numbers like the image size need to be constants.
Try not to code in Label sizes, instead let the tkinter layout manage that.
I/O operations (getting feeds or images from the web) needs to be threaded so the UI is not locked up during (not implemented here)
`if address:` is equivalent to `if len(address) > 0:`
why do you use a dictionary to make a list for 'feeds'? just use a normal list.
'''

import feedparser
from bs4 import BeautifulSoup
import tkinter as tk
import webbrowser
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
from functools import partial

IMG_SIZE = (550, 350)
FEEDS_FILE = 'feeds.txt'

# checks feeds.txt, get's the data and creates a dictionary with data for each article
def get_data():
    with open(FEEDS_FILE) as file:
        feeds = []
        for line in file.readlines():
            d = feedparser.parse(line)

            if d.version == 'atom10':
                for entry in d.entries:
                    soup = BeautifulSoup(str(entry.content), "html.parser")
                    try:
                        image = soup.find('img')['src']
                        feeds.append((d.feed.title, entry.title, image, soup.find('p').get_text(), entry.link))
                    except TypeError:
                        feeds.append((d.feed.title, entry.title, '', soup.find('p').get_text(), entry.link))

            if d.version == 'rss20':
                for entry in d.entries:
                    soup = BeautifulSoup(str(entry.description), "html.parser")
                    try:
                        image = soup.find('img')['src']
                        feeds.append((d.feed.title, entry.title, image, entry.description, entry.link))
                    except TypeError:
                        feeds.append((d.feed.title, entry.title, '', entry.description, entry.link))
    return feeds

# adding new feeds to feeds.txt
class AddFeed(tk.Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Add New Feed')

        self.add_text = tk.Entry(self)
        self.add_text.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        add_button = tk.Button(self, text='Add Feed', command=self.add_feed)
        add_button.grid(row=0, column=3, padx=5, pady=5)

        # the following make a 'modal window', in other words it blocks the main window
        self.transient(master) # set to be on top of the main window
        self.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        master.wait_window(self) # pause anything on the main window until this one closes

    def add_feed(self):
        with open(FEEDS_FILE, 'a') as feed_file:
            feed_file.write(self.add_text.get() + '\n')
        self.destroy()
        self.master.load_feeds()

# removing feeds from feeds.txt
class RemoveFeed(tk.Toplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Remove RSS Feed')

        desc = tk.Label(self, text='Click on URL to remove it')
        desc.pack()

        self.buttons = {}
        with open(FEEDS_FILE) as all_feeds:
            for address in all_feeds.read().splitlines():
                if address:
                    feed_button = tk.Button(self, text=address, command=partial(self.delete_feed, address))
                    feed_button.pack()
                    self.buttons[address] = feed_button

        self.transient(master)
        self.grab_set()
        master.wait_window(self)

    def delete_feed(self, to_delete):
        print(to_delete)
        with open(FEEDS_FILE, 'r') as read:
            lines = read.read().splitlines()
        lines.remove(to_delete)
        with open(FEEDS_FILE, 'w') as write:
            write.write('\n'.join(lines))
            write.write('\n') # trailing newline is tradition and required for append mode
        self.buttons.pop(to_delete).destroy()

class MainWindow(tk.Tk):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title('RSS Reader')

        self.curr_text = tk.StringVar()
        self.curr_text.set('Select Article Above')

        self.listbox = tk.Listbox(self, width=100, selectmode=tk.SINGLE)
        self.listbox.grid(row=1, sticky='we', columnspan=2)
        self.grid_columnconfigure(0, weight=1)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        txt = tk.Label(self, textvariable=self.curr_text, wraplength=550, anchor=tk.W, justify=tk.LEFT)
        txt.grid(row=10, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

        self.img_lbl = tk.Label(self)
        self.img_lbl.grid(row=15, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

        self.open_btn = tk.Button(self, text='Visit Website')
        self.open_btn.grid(row=20, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

        self.loading_lbl = tk.Label(self, text="LOADING FEEDS", font=('', '20'))
        self.loading_lbl.place(relx=.5, rely=.5, anchor=tk.CENTER)

        menubar = tk.Menu(master)
        menubar.add_command(label="Add RSS Feed", command=partial(AddFeed, self))
        menubar.add_command(label="Remove RSS Feed", command=partial(RemoveFeed, self))
        menubar.add_command(label="Quit!", command=self.quit)

        self.config(menu=menubar)

        self.after(100, self.load_feeds) # draw the GUI and then start loading the feeds (give the user something to see)

    def load_feeds(self):
        self.feeds = get_data()
        for key, feed in enumerate(self.feeds):
            self.listbox.insert(key, '{0} : {1}'.format(*feed))
            #~ self.listbox.insert(key, ' : '.join([str(feed[0]), str(feed[1])]))
        self.loading_lbl.destroy()

    def open_url(self, index):
        webbrowser.open_new_tab(self.feeds[index][4])

    def on_select(self, event):
        index = int(event.widget.curselection()[0])

        self.curr_text.set(self.feeds[index][3])
        image_url = self.feeds[index][2]

        # adding a label with image for the article
        if image_url:
            with urllib.request.urlopen(image_url) as u:
                raw_data = u.read()
            im = Image.open(BytesIO(raw_data))
            resize = im.resize(IMG_SIZE, Image.ANTIALIAS)
            image = ImageTk.PhotoImage(resize)
        else:
            image = tk.PhotoImage() # no image; load a blank image
        self.img_lbl.config(image=image)
        self.img_lbl.image = image

        self.open_btn.config(command=partial(self.open_url, index))

if __name__ == '__main__':
    window = MainWindow()
    window.mainloop()

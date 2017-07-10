import feedparser
from bs4 import BeautifulSoup
from tkinter import *
import webbrowser
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO


# checks feeds.txt, get's the data and creates a dictionary with data for each article
def get_data():

    with open('feeds.txt', 'r') as file:
        feeds = {}
        x = 1

        for line in file.readlines():

            d = feedparser.parse(line)

            if d.version == 'atom10':
                for entry in d.entries:
                    soup = BeautifulSoup(str(entry.content), "html.parser")
                    try:
                        image = soup.find('img')['src']
                        feeds[x] = (d.feed.title, entry.title, image, soup.find('p').get_text(), entry.link)
                    except TypeError:
                        feeds[x] = (d.feed.title, entry.title, '', soup.find('p').get_text(), entry.link)
                    x += 1

            if d.version == 'rss20':
                for entry in d.entries:
                    soup = BeautifulSoup(str(entry.description), "html.parser")
                    try:
                        image = soup.find('img')['src']
                        feeds[x] = (d.feed.title, entry.title, image, entry.description, entry.link)
                    except TypeError:
                        feeds[x] = (d.feed.title, entry.title, '', entry.description, entry.link)

                    x += 1
    return feeds

# adding new feeds to feeds.txt
def add_feed_window():
    add_window = Tk()
    add_window.title('Add New Feed')

    entry_text = StringVar()
    add_text = Entry(add_window, textvariable=entry_text)
    add_text.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

    def add_feed():
        with open('feeds.txt', 'a') as feed_file:
            feed_file.write(add_text.get() + '\n')
        add_window.destroy()

    add_button = Button(add_window, text='Add Feed', command=add_feed)
    add_button.grid(row=0, column=3, padx=5, pady=5)

    add_window.mainloop()

# removing feeds from feeds.txt
def remove_feed():
    remove_window = Tk()
    remove_window.title('Remove RSS Feed')

    def delete_feed(to_delete):
        print(to_delete)
        with open('feeds.txt', 'r') as read:
            lines = read.readlines()
            removed_breakline = [i.replace('\n', '') for i in lines]
        with open('feeds.txt', 'w') as write:
            for feed in removed_breakline:
                if feed != to_delete.strip():
                    write.write(feed + '\n')

    desc = Label(remove_window, text='Click on URL to remove it')
    desc.pack()

    with open('feeds.txt', 'r') as all_feeds:
        for address in all_feeds:
            if len(address) > 0:
                feed_button = Button(remove_window, text=address, command=lambda i=address: delete_feed(i+'\n'))
                feed_button.pack()

    remove_window.mainloop()


def main_window():

    feeds = get_data()

    window = Tk()
    window.title('RSS Reader')

    v = StringVar()
    v.set('Select Article Above')

    txt = Label(window, textvariable=v, wraplength=550, anchor=W, justify=LEFT)
    txt.grid(row=10, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

    def on_select(evt):
        labels = []
        w = evt.widget
        index = int(w.curselection()[0])

        def open_url():
            webbrowser.open_new_tab(feeds[index + 1][4])

        v.set(feeds[index + 1][3])
        image_url = feeds[index + 1][2]

        # adding a label with image for the article
        if image_url:
            with urllib.request.urlopen(image_url) as u:
                raw_data = u.read()
            im = Image.open(BytesIO(raw_data))

            resize = im.resize((550, 350), Image.ANTIALIAS)

            image = ImageTk.PhotoImage(resize)
            img = Label(window, image=image, width=500, height=300)
            img.image = image
            img.grid(row=15, column=0, padx=5, pady=5, sticky='swe', columnspan=2)
            labels.append(img)
        else:
            for label in labels:
                label.destroy()

        link = Button(window, text='Visit Website', command=open_url)
        link.grid(row=20, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

    menubar = Menu(window)
    menubar.add_command(label="Add RSS Feed", command=add_feed_window)
    menubar.add_command(label="Remove RSS Feed", command=remove_feed)
    menubar.add_command(label="Quit!", command=window.quit)

    listbox = Listbox(window, width=100, selectmode=SINGLE)
    listbox.grid(row=1, sticky='we', columnspan=2)
    window.grid_columnconfigure(0, weight=1)
    listbox.bind('<<ListboxSelect>>', on_select)

    for key in feeds:
        listbox.insert(key, ' : '.join([str(feeds[key][0]), str(feeds[key][1])]))

    window.config(menu=menubar)
    window.mainloop()


main_window()

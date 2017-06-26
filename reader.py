import feedparser
from bs4 import BeautifulSoup
from tkinter import *
import webbrowser


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
                        feeds[x] = (d.feed.title, entry.title, soup.find('img')['src'], soup.find('p').get_text(), entry.link)
                    except TypeError as e:
                        feeds[x] = (d.feed.title, entry.title, 'no_img', soup.find('p').get_text(), entry.link)
                    x += 1

            if d.version == 'rss20':
                for entry in d.entries:
                    soup = BeautifulSoup(str(entry.description), "html.parser")
                    try:
                        image = soup.find('img')['src']
                        feeds[x] = (d.feed.title, entry.title, image, entry.description, entry.link)
                    except TypeError as e:
                        feeds[x] = (d.feed.title, entry.title, 'no_img', entry.description, entry.link)

                    x += 1
    return feeds


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


def remove_feed():
    remove_window = Tk()
    remove_window.title('Remove RSS Feed')

    def delete_feed(to_delete):
        print(to_delete)
        with open('feeds.txt', 'r') as read:
            lines = read.readlines()
            removed_breakline = [i.replace('\n','') for i in lines]
            print(removed_breakline)
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
            w = evt.widget
            index = int(w.curselection()[0])

            def open_url():
                webbrowser.open_new_tab(feeds[index + 1][4])

            v.set(feeds[index + 1][3])

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
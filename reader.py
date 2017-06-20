import feedparser
from bs4 import BeautifulSoup
from tkinter import *
import webbrowser


with open('feeds.txt','r') as file:

    feeds = {}
    x = 1

    for line in file.readlines():

        d = feedparser.parse(line)

        if d.version == 'atom10':
            for entry in d.entries:
                soup = BeautifulSoup(str(entry.content), "html.parser")
                try:
                    image = soup.find('img')['src']
                    feeds[x] = (
                    d.feed.title, entry.title, soup.find('img')['src'], soup.find('p').get_text(), entry.link)
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


window = Tk()
window.title('RSS Reader')

v = StringVar()
v.set('Select Article Above')
txt = Label(window, textvariable=v, wraplength=550, anchor=W, justify=LEFT)
txt.grid(row=10, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

def on_select(evt):

    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)

    # print('You selected item %d: "%s"' % (index, value))
    # print(feeds[index+1][3])

    def open_url():
        webbrowser.open_new_tab(feeds[index + 1][4])

    v.set(feeds[index+1][3])
    print(v)

    link = Button(window, text='Visit Website', command=open_url)
    link.grid(row=20, column=0, padx=5, pady=5, sticky='swe', columnspan=2)

menubar = Menu(window)
menubar.add_command(label="Refresh")
menubar.add_command(label="Add RSS Feed")
menubar.add_command(label="Remove RSS Feed")
menubar.add_command(label="Quit!", command=window.quit)

listbox = Listbox(window, width=100,  selectmode=SINGLE)
listbox.grid(row=1, sticky='we', columnspan=2)
window.grid_columnconfigure(0,weight=1)
listbox.bind('<<ListboxSelect>>', on_select)

for key in feeds:
    listbox.insert(key, ' : '.join([str(feeds[key][0]), str(feeds[key][1])]))

window.config(menu=menubar)
window.mainloop()
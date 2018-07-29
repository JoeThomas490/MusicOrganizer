from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.messagebox import showinfo

import tkinter as tk

import os

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

class TreeView:
    def __init__(self,master):
        self.master = master

        self.treeviewPopup = None

        self.treeview = ttk.Treeview(self.master.mainframe, selectmode='browse')
        self.treeview.bind("<Double-1>", self.OnDoubleClick)

        self.vsb = ttk.Scrollbar(self.master.mainframe, orient="vertical", command=self.treeview.yview)
        self.vsb.grid(column = 2, row=0, sticky=(N,S))

        self.treeview.configure(yscrollcommand=self.vsb.set)

        self.treeview['columns'] = ('name', 'artist', 'title')
        self.treeview.heading("#0", text="Sources", anchor='w')
        self.treeview.column("#0", anchor='w', minwidth = 0, width = 1)
        self.treeview.heading('name', text='File Name')
        self.treeview.column('name', anchor ='center', width= 200)
        self.treeview.heading('artist', text='Artist Tag')
        self.treeview.column('artist', anchor ='center', width= 100)
        self.treeview.heading('title', text='Title Tag')
        self.treeview.column('title', anchor ='center', width= 100)
        self.treeview.grid(stick = (N,S,W,E), column = 0, row = 0, columnspan=2)
        self.treeview.columnconfigure(0, weight=1)
        self.treeview.rowconfigure(0, weight=1)

    def OnDoubleClick(self,event):
        item = self.treeview.item(self.treeview.focus())
        if item["values"] is "":
            return

        columnNum = self.treeview.identify_column(event.x)[1]
        columnNum = int(columnNum)

        if columnNum is not 2 and columnNum is not 3:
            return

        selectedItem = item["values"][int(columnNum)-1]

        if self.treeviewPopup is None:
            self.treeviewPopup = TreeViewPopup(self, item["values"][0],selectedItem,columnNum)

    def DeletePopup(self):
        self.treeviewPopup.window.destroy()
        self.treeviewPopup = None

    def ConfirmPopupEntry(self, fileName, columnNum, entry):

        audioFile = self.master.audioFileList[fileName]

        #Change ARTIST tag
        if columnNum is 2:
            audioFile["TPE1"] = TPE1(encoding=3, text=entry)
            title = self.treeview.item(fileName)["values"][2]
            self.treeview.item(fileName, values=(fileName, entry, title))

        #Change TITLE tag
        if columnNum is 3:
            audioFile["TIT2"] = TIT2(encoding=3, text=entry)
            artist = self.treeview.item(fileName)["values"][1]
            self.treeview.item(fileName, values=(fileName, artist, entry))

        self.DeletePopup()

        audioFile.save()

    def ClearTreeView(self):
        self.treeview.delete(*self.treeview.get_children())
        self.master.audioFileList.clear()

    def Populate(self):
        
        self.ClearTreeView()
        counter = 0

        for subdir, dirs, files in os.walk(self.master.workingDirectory):
            for file in files:

                filePath = subdir + os.sep + file

                if(filePath.endswith(".mp3")):
                    fileName = os.path.basename(filePath).split(".mp3")[0]
                    try:
                        print("Loading file : " + filePath)
                        audioFile = ID3(filePath)
                        self.master.audioFileList[fileName] = audioFile

                    except IOError:
                        print("Cannot find file!")
                        raise

                    artistName = StringVar()
                    songName = StringVar()

                    if audioFile is not None:
                        if "TPE1" in audioFile:
                            artistName = audioFile["TPE1"]
                        else:
                            artistName = "None"

                        if "TIT2" in audioFile:
                            songName = audioFile["TIT2"]
                        else:
                            songName = "None"

                   

                    self.treeview.insert('', 'end', fileName, text=filePath, values=(fileName, artistName, songName))

class TreeViewPopup:
    def __init__(self, master, fileName, selectedItem,columnNum):

        self.master = master

        self.window = tk.Toplevel()
        self.window.wm_title("Edit Tag")
        self.window.wm_attributes("-topmost",1)

        self.window.protocol("WM_DELETE_WINDOW", self.master.DeletePopup)

        self.window.geometry("%dx%d%+d%+d" % (300, 100, 150, 250))

        self.tagLbl = tk.Label(self.window, text="Tag")
        self.tagLbl.grid(row=0, column=0)

        self.tagEntry = tk.Entry(self.window)
        self.tagEntry.grid(row=0, column=1, sticky=(N,E))
        self.tagEntry.delete(0,END)
        self.tagEntry.insert(0, selectedItem)
        self.tagEntry.focus_set()

        self.confirmBtn = ttk.Button(self.window, text="Confirm", command=lambda:self.master.ConfirmPopupEntry(fileName, columnNum, self.tagEntry.get()))
        self.confirmBtn.grid(row=1, column=0, sticky=(S,W))

        self.cancelBtn = ttk.Button(self.window, text="Cancel", command=lambda:self.master.DeletePopup())
        self.cancelBtn.grid(row=1, column= 1, sticky=(S,E))        

        for child in self.window.winfo_children(): child.grid_configure(padx=5, pady=5)

        self.window.bind("<Return>", (lambda event:self.master.ConfirmPopupEntry(fileName, columnNum, self.tagEntry.get())))
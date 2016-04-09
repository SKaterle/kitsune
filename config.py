import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


class Configuration:
    def __init__(self, parent):
        self.__parent = parent
        self.managaPath = StringVar()
        self.downloadPath = StringVar()
        self.chapterPool = IntVar()
        self.pagePool = IntVar()
        self.__configPath = os.path.dirname(os.path.realpath(__file__))
        self.__confFile = "%s\\%s" % (self.__configPath, "config.conf")
        if os.path.isfile(self.__confFile):
            self.__readConf()
        else:
            handle = open(self.__confFile, "w")
            handle.write("managaPath=\n")
            handle.write("downloadPath=\n")
            handle.write("chapterPool=6\n")
            handle.write("pagePool=10\n")
            handle.close()
            handle = None
            self.__readConf()

        if self.managaPath.get() == "":
            self.configFrame()

    def __readConf(self):
        ctrl = [line.rstrip('\n') for line in open(self.__confFile)]
        for k in ctrl:
            v = k.split("=")
            if "managaPath" in v[0]:
                self.managaPath.set(v[1])
            if "downloadPath" in v[0]:
                self.downloadPath.set(v[1])
            if "chapterPool" in v[0]:
                self.chapterPool.set(v[1])
            if "pagePool" in v[0]:
                self.pagePool.set(v[1])

        if not os.path.isdir(self.managaPath.get()):
            self.managaPath.set("")

        if not os.path.isdir(self.downloadPath.get()):
            self.downloadPath.set("")

    def __saveConfiguration(self):
        handle = open(self.__confFile, "w")
        handle.write("managaPath=%s\n" % self.managaPath.get())
        handle.write("downloadPath=%s\n" % self.downloadPath.get())
        handle.write("chapterPool=%s\n" % self.chapterPool.get())
        handle.write("pagePool=%s\n" % self.pagePool.get())
        handle.close()
        handle = None

    def configFrame(self):
        for widget in self.__parent.winfo_children():
            widget.grid_remove()

        # Base Configuration
        ttk.Label(self.__parent, text="Configuration", anchor=CENTER, relief=RAISED)\
            .grid(row=0, column=0, columnspan=3, sticky=(N, W, E))

        # Manga Folder
        ttk.Label(self.__parent, text="Manga Folder:", width=20).grid(row=1, column=0, sticky=(N, W))
        ttk.Label(self.__parent, textvariable=self.managaPath,  width=40).grid(row=1, column=1, sticky=(N, W))
        ttk.Button(self.__parent, text='Select Folder', command=lambda: self.__askdirectory(self.managaPath))\
            .grid(row=1, column=2, sticky=(N, E))
        # Download Folder
        ttk.Label(self.__parent, text="Download Folder:", width=20).grid(row=2, column=0, sticky=(N, W))
        ttk.Label(self.__parent, textvariable=self.downloadPath,  width=40).grid(row=2, column=1, sticky=(N, W))
        ttk.Button(self.__parent, text='Select Folder', command=lambda: self.__askdirectory(self.downloadPath))\
            .grid(row=2, column=2, sticky=(N, E))

        # Adv Configuration
        # valCmd = (self.__parent.register(self.__validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # ttk.Label(self.__parent, text="Advanced", anchor=CENTER, relief=RAISED)\
        #     .grid(row=3, column=0, columnspan=3, sticky=(N, W, E))
        # ttk.Label(self.__parent, text="Chapter Pool:", width=20).grid(row=4, column=0, sticky=(N, W))
        # Entry(self.__parent, validate = 'key', validatecommand = valCmd, width=4, textvariable=self.chapterPool)\
        #     .grid(row=4, column=1, sticky=(N, W))
        # ttk.Label(self.__parent, text="Page Pool:", width=20).grid(row=5, column=0, sticky=(N, W))
        # Entry(self.__parent, validate = 'key', validatecommand = valCmd, width=4, textvariable=self.pagePool)\
        #     .grid(row=5, column=1, sticky=(N, W))

        # Save Config
        ttk.Button(self.__parent, text='Save Configuration', command=self.__saveConfiguration)\
            .grid(row=99, column=2, sticky=(N, E))
        return

    def __askdirectory(self, strvar):
        __dir_opt = options = {}
        if strvar.get() == "":
            options['initialdir'] = self.__configPath
        else:
            options['initialdir'] = strvar.get()
        options['mustexist'] = True
        options['parent'] = self.__parent
        options['title'] = 'Select Folder'
        strvar.set(filedialog.askdirectory(**__dir_opt))
        return

    def __validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if text in '0123456789':
            return True
        else:
            return False
import os, shutil
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as tkst
from adapter.repository import MangaRepository


class LocalMangas:
    def __init__(self, parent, mangaPath, dlPath, child, mangaList):
        # definitions
        self.__parent = parent
        self.__mangaPath = mangaPath
        if len(dlPath) > 0:
            self.__downloadPath = dlPath
        else:
            self.__downloadPath = mangaPath
        self.__txtReport = child
        self.__ctrlfile = "kitsune.txt"
        self.mangaList = mangaList
        #calls
        self.__loadRepository()
        return

    def __outReport(self, text):
        self.__txtReport.insert(END, text)
        self.__txtReport.update()
        self.__txtReport.see(END)
        return

    def __loadRepository(self):
        ttk.Label(self.__parent, text="Local Mangas", width=80).grid(row=0, column=0, sticky=(N, W))
        self.__lst_manga = ttk.Treeview(self.__parent, columns=("Manga", "Chapter"), height=10)
        self.__lst_manga.grid(row=1, column=0,  sticky=(N, W, S, E))
        self.__lst_manga['show'] = "headings"
        self.__lst_manga.column("Manga", minwidth=200, width=420, stretch=NO, anchor="w")
        self.__lst_manga.heading("Manga", text="Manga", anchor="w")
        self.__lst_manga.column("Chapter", minwidth=0, width=80, stretch=NO, anchor="center")
        self.__lst_manga.heading("Chapter", text="Chapter(s)", anchor="center")
        self.__loadChapters()
        return

    def __loadChapters(self):
        self.__outReport("Loading Chapters.\n")
        for key in self.__get_subdir(self.__mangaPath):
            item = MangaRepository()
            item.mangaName = key
            item.savePath = self.__downloadPath
            ctrlpath = os.path.join(self.__mangaPath, key, self.__ctrlfile)
            if os.path.isfile(ctrlpath):
                cmd = dict()
                ctrl = [line.rstrip('\n') for line in open(ctrlpath)]
                for k in ctrl:
                    v = k.split("=")
                    item.adpMangaURL[v[0]] = v[1]
            item.offlineChapters = self.__getChapterList(key)
            self.mangaList[item.mangaName] = item
        self.__lst_manga.delete(*self.__lst_manga.get_children())
        if len(self.mangaList) > 0:
            for key in self.mangaList:
                item = self.mangaList[key]
                self.__lst_manga.insert('',
                                        END,
                                        text=item.mangaName,
                                        values=(item.mangaName, len(item.offlineChapters)))
            l = [(self.__lst_manga.set(k, "Manga"), k) for k in self.__lst_manga.get_children('')]
            l.sort(reverse=False)
            for index, (val, k) in enumerate(l):
                self.__lst_manga.move(k, '', index)
        self.__outReport("Ready.\n")
        return

    def __get_subdir(self, directory):
        return [name for name in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, name))]

    def __getChapterList(self,mangaName):
        chapterList = list()
        for sub in self.__get_subdir(self.__mangaPath + "\\" + mangaName):
            chapterList.append(sub)
        return chapterList

    def __copytree(self, src, dst, symlinks=False, ignore=None):
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        if not os.path.isdir(dst): # This one line does the trick
            os.makedirs(dst)
        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    self.__copytree(srcname, dstname, symlinks, ignore)
                else:
                    # Will raise a SpecialFileError for unsupported file types
                    shutil.copy2(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except:
                pass

    def update(self):
        if self.__mangaPath != self.__downloadPath:
            try:
                self.__copytree(self.__downloadPath, self.__mangaPath)
            except:
                pass
            finally:
                pass
        self.__loadChapters()
        return
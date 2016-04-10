import os, collections
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as tkst
from config import Configuration
from adapter.local import LocalMangas
from adapter.mangareader import MangaReaderNet
from adapter.mangahere import MangaHereCo
from adapter.mangafox import MangaFoxMe
from adapter.repository import MangaRepository


class mainApp:
    def __init__(self, parent, myMangas):
        # Definitions
        self.__myMangas = myMangas
        self.__parent = parent
        self.__config = Configuration(self.__parent)
        # Calls
        ttk.Label(self.__parent, text="Start Up", anchor=CENTER, relief=RAISED).\
            grid(row=1, column=0, sticky=(N, W, E))
        ttk.Label(self.__parent, text="Reading Config\nDone.\nProceed to download.\n", anchor=W).\
            grid(row=2, column=0, sticky=(N, W, E))
        self.__menu()
        if os.path.isdir(self.__config.managaPath.get()):
            self.__download()
        return

    def __menu(self):
        menu = Menu(self.__parent, name='mainMenu')
        self.__parent.config(menu=menu)
        menu.add_command(label="Search", command=self.__search)
        menu.add_command(label="Download", command=self.__download)
        menu.add_command(label="Config", command=self.__config.configFrame)
        menu.add_command(label="Exit", command=self.__parent.quit)
        return

    def __outReport(self, text):
        self.__txtReport.insert(END, text)
        self.__txtReport.update()
        self.__txtReport.see(END)
        return

    def __search(self):
        for widget in self.__parent.winfo_children():
            widget.grid_remove()
        self.__parent.grid()
        ttk.Label(self.__parent, text="Local Map", width=80, relief=RAISED).grid(row=0, column=0, columnspan=4, sticky=(N, W, E))
        self.__lst_manga = ttk.Treeview(self.__parent, height=12, columns=("Adapter", "URL"))
        self.__lst_manga.grid(row=1, column=0, columnspan=4, sticky=(N, W, S, E))
        self.__lst_manga.config(selectmode='browse')
        # self.__lst_manga['show'] = "headings"
        self.__lst_manga.column("Adapter", stretch=YES, anchor="w")
        self.__lst_manga.heading("Adapter", text="Adapter", anchor="w")
        self.__lst_manga.column("URL", stretch=YES, anchor="w")
        self.__lst_manga.heading("URL", text="URL", anchor="w")
        self.__lst_manga.bind("<<TreeviewSelect>>", self.__SelectItem)
        self.__btn_Auto_Map = Button(self.__parent, text="Auto Map", state=DISABLED)
        self.__btn_Auto_Map.grid(row=2, column=1, sticky=(N, E, W))
        self.__btn_Del_Map = Button(self.__parent, text="Del Map", state=DISABLED)
        self.__btn_Del_Map.grid(row=2, column=2, sticky=(N, E, W))
        self.__btn_Save_Map = Button(self.__parent, text="Save Map", command=self.__save_maps)
        self.__btn_Save_Map.grid(row=2, column=3, sticky=(N, E, W))
        ttk.Label(self.__parent, text="Add Manga", width=80, relief=RAISED).grid(row=3, column=0, columnspan=4, sticky=(N, W, E))
        self.__newMangaName = StringVar()
        self.__txtNewMangaName = ttk.Entry(self.__parent, textvariable=self.__newMangaName)
        self.__txtNewMangaName.grid(row=4, column=0, columnspan=3, sticky=(N, E, W))
        self.__btn_AddManga = Button(self.__parent, text="Add Manga", command=self.__add_new_manga)
        self.__btn_AddManga.grid(row=4, column=3, sticky=(N, E, W))
        self.__seach_build_list()

    def __seach_build_list(self):
        if len(self.__myMangas) > 0:
            for key in self.__myMangas:
                item = self.__myMangas[key]
                self.__lst_manga.insert('',
                                        END,
                                        iid=item.mangaName,
                                        text=item.mangaName,
                                        values=(item.mangaName, "", ""))
                if item.adpMangaURL:
                    for adpt in item.adpMangaURL:
                        if adpt:
                            self.__lst_manga.insert(item.mangaName,
                                            END,
                                            text=adpt,
                                            values=(adpt, item.adpMangaURL[adpt]))
            l = [(self.__lst_manga.set(k, "Adapter"), k) for k in self.__lst_manga.get_children('')]
            l.sort(reverse=False)
            for index, (val, k) in enumerate(l):
                self.__lst_manga.move(k, '', index)
            self.__lst_manga.update()
        return

    def __add_new_manga(self):
        newItem = MangaRepository
        newItem.mangaName = self.__newMangaName.get()
        newItem.adpMangaURL = dict()
        self.__newMangaName.set("")
        lstAdapter = list()
        lstAdapter.append(MangaReaderNet())
        lstAdapter.append(MangaHereCo())
        lstAdapter.append(MangaFoxMe())
        for adapter in lstAdapter:
            for key, value in (adapter.checkMangaExist(newItem.mangaName)).items():
                newItem.adpMangaURL[key] = value
        self.__myMangas[newItem.mangaName] = newItem
        self.__seach_build_list()
        return

    def __save_maps(self):
        self.__btn_Auto_Map.config(state=DISABLED)
        self.__btn_Del_Map.config(state=DISABLED)
        self.__btn_AddManga.config(state=DISABLED)
        self.__btn_Save_Map.config(state=DISABLED)
        self.__parent.update()
        mdir = self.__config.managaPath.get()
        for parent in self.__lst_manga.get_children():
            fdir = os.path.normpath(os.path.join(mdir, self.__lst_manga.item(parent)['text']))
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            ctrl = os.path.normpath(os.path.join(fdir, "kitsune.txt"))
            if os.path.isfile(ctrl):
                os.remove(ctrl)
            print(ctrl)
            handle = open(ctrl, "w")
            for child in self.__lst_manga.get_children(parent):
                key = self.__lst_manga.item(child)['values'][0]
                value = self.__lst_manga.item(child)['values'][1]
                handle.write("%s=%s\n" % (key, value))
            handle.close()
            handle = None
        self.__seach_build_list()
        return

    def __SelectItem(self, event):
        self.__selected_Item = self.__lst_manga.selection()[0]
        self.__btn_Auto_Map.config(state=NORMAL)
        # self.__btn_Del_Map.config(state=NORMAL)
        return

    def __download(self):
        for widget in self.__parent.winfo_children():
            widget.grid_remove()
        # add frames
        ttk.Label(self.__parent, text="Local Mangas", width=80).grid(row=0, column=0, sticky=(N, W))
        self.__txtReport = tkst.ScrolledText(self.__parent, wrap=WORD, width=60, height=10)
        self.__txtReport.grid(row=99, column=0, sticky=(N, E, S))
        # get local mangas and build listings
        self.__outReport("Loading local managas.\n")
        self.__adp_local = LocalMangas(self.__parent, self.__config.managaPath.get(), self.__config.downloadPath.get(), self.__txtReport, self.__myMangas)
        self.__btn_start_download = ttk.Button(self.__parent, text="Start Download", command=self.__start_download)
        self.__btn_start_download.grid(row=10, column=0, sticky=(N, W, E, S))
        self.__progress = ttk.Progressbar(self.__parent, orient="horizontal", mode="determinate")
        self.__progress.grid(row=20, column=0, sticky=(N, E, W))
        return

    def __start_download(self):
        self.__btn_start_download.config(state=DISABLED)
        self.__outReport("Starting Download\n")
        lstAdapter = list()
        lstAdapter.append(MangaReaderNet(self.__adp_local.mangaList, self.__txtReport, self.__progress))
        lstAdapter.append(MangaHereCo(self.__adp_local.mangaList, self.__txtReport, self.__progress))
        lstAdapter.append(MangaFoxMe(self.__adp_local.mangaList, self.__txtReport, self.__progress))
        self.__progress['maximum'] = len(self.__adp_local.mangaList)
        for adapter in lstAdapter:
            self.__progress['value'] = 0
            adapter.start()
            self.__adp_local.update()
        self.__btn_start_download.config(state=NORMAL)
        return


def main():
    glb_myMangas = dict()
    root = Tk()
    root.title("Kitsune - Manga Sync")
    app = mainApp(root, glb_myMangas)
    root.mainloop()

if __name__ == '__main__':
    main()
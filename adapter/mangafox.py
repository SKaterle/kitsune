import os, shutil, requests, collections
from bs4 import BeautifulSoup
from multiprocessing import Pool
from tkinter import *
from tkinter import ttk


class MangaFoxMe:
    def __init__(self, lstMangas=None, report=None, pbar=None):
        self.__url = "http://mangafox.me/manga/"
        self.__ctrl =  "mangafoxme"
        self.__prittyName = "MangaFox"
        self.__onlineMangaChapter = dict()
        self.__imgList = dict()
        self._listMangas = lstMangas
        self.__txtReport = report
        if report:
            self.__outReport("Adapter %s loaded.\n" % self.__prittyName)
        self.__progress = pbar
        return

    def __outReport(self, text):
        self.__txtReport.insert(END, text)
        self.__txtReport.update()
        self.__txtReport.see(END)
        return

    def __buildURI(self, manga):
        uri = str(self.__url + re.sub("[ -,]", "_", manga)).lower()
        uri = re.sub("[()!']", "", uri)
        while "__" in uri:
            uri = uri.replace("__", "_")
        return uri

    def start(self):
        self.__outReport("Checking OnLine Chapters @%s.\n" % self.__prittyName)
        for key in self._listMangas:
            self.__progress['value'] += 1
            self.__progress.update()
            self._listMangas[key].onlineChapters = self.__checkChapter(self._listMangas[key])
            if len(self._listMangas[key].onlineChapters) > 0:
                self.__outReport("-- Manga '%s' has %d new chapter(s) avail.\n" %
                                 (self._listMangas[key].mangaName, len(self._listMangas[key].onlineChapters)))
                self.__downloadChapters(key)
        return

    def checkMangaExist(self, mangaName):
        result = dict()
        result[self.__ctrl] = "#skip"
        uri = self.__buildURI(mangaName)
        response = requests.get(uri)
        if response.status_code == requests.codes.ok:
            result[self.__ctrl] = uri
        return result

    def __checkChapter(self,item):
        resultChapters = dict()
        if self.__ctrl in item.adpMangaURL:
            for key, value in self.__getChapters(item.adpMangaURL[self.__ctrl]).items():
                if key not in item.offlineChapters:
                    resultChapters[key] = value
        else:
            self.__outReport("-- Error: Manga '%s' is not mapped to the adapter.\n" % item.mangaName)
        return resultChapters

    def __getChapters(self,uri):
        result = dict()
        if "#skip" not in uri:
            response = requests.get(uri)
            if response.status_code == requests.codes.ok:
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find_all('ul', attrs={'class': 'chlist'})
                for row in table:
                    row = str(row)
                    row = row[row.find('class="tips"') + 19: row.find('title="') - 2].replace("/1.html", "")
                    chapter = row
                    chapter = (chapter[chapter.rfind('/', 0, len(chapter) - 1):]).replace('/', '').replace('c', 'Chapter ')
                    result[chapter] = row
        return result

    def __downloadChapters(self, mangaKey):
        if len(self._listMangas[mangaKey].onlineChapters) == 0:
            return
        else:
            od = collections.OrderedDict(sorted(self._listMangas[mangaKey].onlineChapters.items()))
            self.__imgList.clear()
            for key, value in od.items():
                self.__outReport("---- Get pages for %s > " % key)
                key = os.path.normpath(os.path.join(self._listMangas[mangaKey].savePath, self._listMangas[mangaKey].mangaName, key))
                self.__imgList = self._downChapter(key, value)
                self.__outReport("%s pages.\n" % len(self.__imgList))
                if len(self.__imgList) > 0:
                    for key, value in self.__imgList.items():
                        self._savePage(key, value)

        return

    def _downChapter(self, *kwargs):
        imgList = dict()
        uri = kwargs[1]
        fDir = kwargs[0]
        count = 0
        response = requests.get(uri)
        if response.status_code == requests.codes.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find('select', attrs={'onchange': 'change_page(this)'})
            if table == None:
                return imgList
            for row in table.findAll('option'):
                row = str(row)
                if "Comments" not in row:
                    count += 1
                    response = requests.get(uri + "/" + str(count).strip() + ".html")
                    if response.status_code == requests.codes.ok:
                        soup = BeautifulSoup(response.text, "html.parser")
                        table = soup.find('img', attrs={'id': 'image'})
                        row = str(table)
                        row = row[row.find('src=') + 5:]
                        row = row[:row.find('"') - 1]
                        imgList[fDir + "\\" + (str("0000" + str(count).strip())[-3:]) + row[row.rfind('.'):]] = row
        del response
        return imgList

    def _savePage(self, *kwargs):
        fname = kwargs[0]
        uri = kwargs[1]
        try:
            os.makedirs(fname[:fname.rfind('\\')])
        except:
            pass
        try:
            with open(fname, 'wb') as handle:
                response = requests.get(uri, stream=True)
                if response.ok:
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)
                del response
                handle.close()
        except:
            if os.path.exists(fname):
                os.remove(fname)
            try:
                with open(fname, 'wb') as handle:
                    response = requests.get(uri, stream=True)
                    if response.ok:
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
                    del response
                    handle.close()
            except:
                pass
        finally:
            pass
        return
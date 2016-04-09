import os, shutil, requests, multiprocessing, collections
from bs4 import BeautifulSoup
from multiprocessing import Pool
from tkinter import *


class MangaReaderNet:
    def __init__(self, lstMangas, report, pbar):
        self.__url = "http://www.mangareader.net/"
        self.__ctrl = "mangareadernet"
        self.__prittyName = "MangaReader"
        self.__imgList = dict()
        self._listMangas = lstMangas
        self.__txtReport = report
        self.__outReport("Adapter %s loaded.\n" % self.__prittyName)
        self.__progress = pbar
        return

    def __outReport(self, text):
        self.__txtReport.insert(END, text)
        self.__txtReport.update()
        self.__txtReport.see(END)
        return

    def start(self):
        self.__outReport("Checking OnLine Chapters @%s.\n" % self.__prittyName)
        for key in self._listMangas:
            self.__progress['value'] += 1
            self.__progress.update()
            self._listMangas[key].onlineChapters = self.__checkChapter(self._listMangas[key])
            if len(self._listMangas[key].onlineChapters) > 0:
                self.__outReport("-- Manga '%s' has %d new chapter(s) avail.\n" %
                                 (key, len(self._listMangas[key].onlineChapters)))
                self.__downloadChapters(key)
        return

    def __buildURI(self, manga):
        uri = str(self.__url + re.sub("[ (),]", "-", manga)).lower()
        uri = uri.replace("'","")
        while "--" in uri:
            uri = uri.replace("--", "-")
        return uri

    def __checkMangaExist(self, mangaName):
        uri = self.__buildURI(mangaName)
        response = requests.get(uri)
        if response.status_code == requests.codes.ok:
            return uri
        else:
            return "#skip"

    def __checkChapter(self, item):
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
                table = soup.find('table', attrs={'id':'listing'})
                for row in table.findAll('a'):
                    row = str(row).replace('</a>', '').replace('<a ', '').split('>')
                    begin = str(row).find('"') + 2
                    chapter = re.sub('[^0-9.]+', '', row[1])
                    if "." in chapter:
                        sanity = chapter.split(".")
                        if len(sanity[0]) == 0:
                            chapter = sanity[1]
                    result["Chapter 000"[:-len(chapter)] + chapter] = self.__url + str(row)[begin:str(row).find('"', begin)]
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

            # pool = Pool(processes=16)  # between 16 to 20 simultaneously downloads seems to be possible
            # pool.map(self._savePage,self.__imgList.items())
            # pool.close()
            # pool.join()
        return

    def _downChapter(self, *kwargs):
        imgList = dict()
        uri = kwargs[1]
        fDir = kwargs[0]
        response = requests.get(uri)
        if response.status_code == requests.codes.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find('select', attrs={'id':'pageMenu'})
            pages = list()
            for row in table.findAll('option'):
                first = str(row).find("\"") + 1
                pages.append(str(row)[first:str(row).find("\"", first)])
            count = 0
            for page in pages:
                count += 1
                if page == "selected":
                    img = str(soup.find('div', attrs={'id':'imgholder'}))
                    start = img.find("src=\"") + 5
                    end = img.find("\"", start)
                    img = img[start:end]
                    imgList[fDir + "\\" + str("0000" + str(count))[-3:] + img[-4:]] = img
                else:
                    response = requests.get(self.__url[:-1] + page)
                    if response.status_code == requests.codes.ok:
                        soup = BeautifulSoup(response.text, "html.parser")
                        img = str(soup.find('div', attrs={'id':'imgholder'}))
                        start = img.find("src=\"") + 5
                        end = img.find("\"", start)
                        img = img[start:end]
                        imgList[fDir + "\\" + str("0000" + str(count))[-3:] + img[-4:]] = img
        del response
        if len(imgList) > 0:
            if os.path.exists(fDir):
                shutil.rmtree(fDir)
            else:
                os.makedirs(fDir)
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
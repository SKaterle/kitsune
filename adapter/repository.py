import collections


class MangaRepository:
    # Data Class for holding manga information
    def __init__(self):
        self.mangaName = ""
        self.offlineChapters = collections.OrderedDict()
        self.adpMangaURL = dict()
        self.onlineChapters = collections.OrderedDict()
        self.savePath = ""
        return

    def _debug(self):
        print("#################### %s" % self.mangaName)
        print(self.adpMangaURL)
        print(self.offlineChapters)
        print(self.onlineChapters)
        print(self.savePath)
        print("####################\n")
        return

    def getMangaValid(self, adapter="#skip"):
        if adapter in self.adpMangaURL:
            if "#skip" in self.adpMangaURL[adapter]:
                return False
            else:
                return True
        else:
            return False
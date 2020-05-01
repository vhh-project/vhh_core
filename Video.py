
class Video():
    def __init__(self, vid, originalFileName, url):
        #print("create instance of Video");
        self.id = vid
        self.originalFileName = originalFileName
        self.url = url
        self.video_format = url.split('.')[-1]

    def printInfo(self):
        print("\n####################################################")
        print("id: " + str(self.id))
        print("originalFileName: " + str(self.originalFileName))
        print("url: " + str(self.url))
        print("####################################################")
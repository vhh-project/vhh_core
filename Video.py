import os
import yaml

class Video(object):
    def __init__(self, config=None):
        print("create instance of Video")

        if (config == None):
            print("You have to specify a valid configuration instance!")

        self.__core_config = config

        self.__id = -1
        self.__originalFileName = "None"
        self.__url = "None"
        self.__video_format = "None"
        self.__file_name = "None"
        self.__download_path = "None"

    def create_video(self, vid, originalFileName, url, download_path):
        #print("create instance of Video");
        self.__id = vid
        self.__originalFileName = originalFileName
        self.__url = url
        self.__video_format = url.split('.')[-1]
        self.__file_name = url.split('/')[-1]
        self.__download_path = download_path

    def download(self, rest_api_instance=None):
        if (rest_api_instance == None):
            print("You have to specify a valid object of class type VhhRestApi to execute the download process!")
            exit()

        ret = rest_api_instance.downloadVideo(self.__url,
                                              str(self.__id),
                                              self.__video_format)
        return ret

    def is_downloaded(self):
        print("Check if video is already available in specified download path: " + str(self.__download_path))
        ret = False

        # get list of videos in download path
        video_list = os.listdir(self.__download_path)
        search_str = str(self.__id) + "." + self.__video_format

        # find video name in list
        if (search_str in video_list):
            print("video is already available ... ")
            ret = True

        return ret

    def cleanup(self):
        print("start cleanup process ... ")

        print("Delete video if available in video_download path ...")
        # get list of videos in download path
        video_list = os.listdir(self.__download_path)
        search_str = str(self.__id) + "." + self.__video_format

        # find video name in list
        if (search_str in video_list):
            print("delete video ... ")
            file_path = os.path.join(self.__download_path, search_str)
            os.remove(file_path)

        print("Delete sbd results if available ...")
        fp = open(self.__core_config.sbd_config_file, 'r')
        sbd_config = yaml.load(fp, Loader=yaml.BaseLoader)
        sbd_results_dir = sbd_config['SbdCore']['PATH_FINAL_RESULTS']
        fp.close()

        search_str = str(self.__id) + ".csv"
        result_file_list = os.listdir(sbd_results_dir)
        if (search_str in result_file_list):
            print("delete sbd results ... ")
            file_path = os.path.join(sbd_results_dir, search_str)
            os.remove(file_path)

        print("Delete stc results if available  ...")
        fp = open(self.__core_config.stc_config_file, 'r')
        stc_config = yaml.load(fp, Loader=yaml.BaseLoader)
        stc_results_dir = stc_config['StcCore']['PATH_FINAL_RESULTS']
        fp.close()

        search_str = str(self.__id) + ".csv"
        result_file_list = os.listdir(stc_results_dir)
        if (search_str in result_file_list):
            print("delete stc results ... ")
            file_path = os.path.join(stc_results_dir, search_str)
            os.remove(file_path)

        print("Delete cmc results if available  ...")

        print("cleanup process successfully finished!")

    def printInfo(self):
        print("\n####################################################")
        print("id: " + str(self.__id))
        print("originalFileName(without extension): " + str(self.__originalFileName))
        print("storage file name (with extension): " + str(self.__file_name))
        print("video_format: " + str(self.__video_format))
        print("url: " + str(self.__url))
        print("download_path: " + str(self.__download_path))
        print("####################################################")
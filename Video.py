import os
import yaml


class Video(object):
    """
    This class represents a video object.
    """

    def __init__(self, config=None):
        """
        Constructor

        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """
        print("create instance of Video")

        if (config == None):
            print("You have to specify a valid configuration instance!")

        self.__core_config = config

        self.id = -1
        self.originalFileName = "None"
        self.url = "None"
        self.video_format = "None"
        self.file_name = "None"
        self.download_path = "None"

    def create_video(self, vid, originalFileName, url, download_path):
        """
        This method is used to fill all properties of a video.

        :param vid: This parameter must hold a valid video id.
        :param originalFileName: This parameter must hold the original filename of a video
        :param url: This parameter must hold the download url of the video.
        :param download_path: This parameter must hold the download path in the local storage.
        """
        #print("create instance of Video");
        self.id = vid
        self.originalFileName = originalFileName
        self.url = url
        self.video_format = url.split('.')[-1]
        self.file_name = url.split('/')[-1]
        self.download_path = download_path

    def download(self, rest_api_instance=None):
        """
        This method is used to download the video into the local storage path.

        :param rest_api_instance: This parameter must hold a valid VhhRestApi object.
        :return: This method returns the download status (true ... successfully downloaded OR false ... download failed).
        """
        if (rest_api_instance == None):
            print("You have to specify a valid object of class type VhhRestApi to execute the download process!")
            exit()

        ret = rest_api_instance.downloadVideo(self.url,
                                              str(self.id),
                                              self.video_format)
        return ret

    def is_downloaded(self):
        """
        This method is used to check if a video is already downloaded.

        :return: This method returns a boolean flag (true ... video already downloaded OR false ... video does not exist).
        """
        print("Check if video is already available in specified download path: " + str(self.download_path))
        ret = False

        # get list of videos in download path
        video_list = os.listdir(self.download_path)
        search_str = str(self.id) + "." + self.video_format

        # find video name in list
        if (search_str in video_list):
            print("video is already available ... ")
            ret = True

        return ret

    def cleanup(self):
        """
        This method is used to cleanup all data related to the corresponding video ID. It deletes the generated results
        of the sbd, stc and cmc plugin as well as the downloaded video file.
        """
        print("start cleanup process ... ")

        print("Delete video if available in video_download path ...")
        # get list of videos in download path
        video_list = os.listdir(self.download_path)
        search_str = str(self.id) + "." + self.video_format

        # find video name in list
        if (search_str in video_list):
            print("delete video ... ")
            file_path = os.path.join(self.download_path, search_str)
            os.remove(file_path)

        print("Delete sbd results if available ...")
        fp = open(self.__core_config.sbd_config_file, 'r')
        sbd_config = yaml.load(fp, Loader=yaml.BaseLoader)
        sbd_results_dir = sbd_config['SbdCore']['PATH_FINAL_RESULTS']
        fp.close()

        search_str = str(self.id) + ".csv"
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

        search_str = str(self.id) + ".csv"
        result_file_list = os.listdir(stc_results_dir)
        if (search_str in result_file_list):
            print("delete stc results ... ")
            file_path = os.path.join(stc_results_dir, search_str)
            os.remove(file_path)

        print("Delete cmc results if available  ...")

        print("cleanup process successfully finished!")

    def printInfo(self):
        """
        This method summarizes all properties of this object and print it to the console.
        """

        print("\n####################################################")
        print("id: " + str(self.id))
        print("originalFileName(without extension): " + str(self.originalFileName))
        print("storage file name (with extension): " + str(self.file_name))
        print("video_format: " + str(self.video_format))
        print("url: " + str(self.url))
        print("download_path: " + str(self.download_path))
        print("####################################################")
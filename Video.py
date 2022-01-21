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
        #print("create instance of Video")

        if (config == None):
            print("You have to specify a valid configuration instance!")

        self.__core_config = config

        self.id = -1
        self.originalFileName = "None"
        self.url = "None"
        self.video_format = "None"
        self.file_name = "None"
        self.download_path = "None"
        self.processed_flags = {}

    def create_video(self, vid, originalFileName, url, download_path, processed_flag_shots, processed_flag_objects, processed_flag_relations, processed_flag_overscan):
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
        self.processed_flags = {
            "shots": processed_flag_shots,
            "objects": processed_flag_objects,
            "relations": processed_flag_relations,
            "overscan": processed_flag_overscan}

    def download(self, rest_api_instance=None, filename = None):
        """
        This method is used to download the video into the local storage path.

        :param rest_api_instance: This parameter must hold a valid VhhRestApi object.
        :return: This method returns the download status (true ... successfully downloaded OR false ... download failed).
        """
        if (rest_api_instance == None):
            print("You have to specify a valid object of class type VhhRestApi to execute the download process!")
            exit()

        if filename is None:
            filename = str(self.id)
        ret = rest_api_instance.downloadVideo(self.url,
                                              filename,
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

    def is_processed(self):
        """
        This method is used to check if a video was already processed by evaluating the processed_flag.

        :return: This method returns a boolean flag (true ... video already processed OR false ... video was not processed in earlier runs).
        """
        return self.processed_flag

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

        # Delte results from SBD, STC, CMC and ODT
        search_str = str(self.id) + ".csv"

        for config_file_path, config_section in zip(
            [self.__core_config.sbd_config_file, self.__core_config.stc_config_file, self.__core_config.cmc_config_file, self.__core_config.odt_config_file], 
            ['SbdCore', 'StcCore', 'CmcCore', 'OdCore']):

            print("Deleting result: ", config_section)
            with open(config_file_path, 'r') as fp:
                config = yaml.load(fp, Loader=yaml.BaseLoader)
                results_dir = config[config_section]['PATH_FINAL_RESULTS']

                result_file_list = os.listdir(results_dir)
                if (search_str in result_file_list):
                    file_path = os.path.join(results_dir, search_str)
                    os.remove(file_path)    

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
        print("processed flags:\n\tSHOTS: {0}\n\tObjects: {1}\n\tRelations: {2}\n\tOverscan: {3}".format(
            self.processed_flags["shots"], self.processed_flags["objects"], self.processed_flags["relations"], self.processed_flags["overscan"]))
        print("####################################################")
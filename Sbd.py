from sbd.SBD import SBD
from sbd.utils import *
from Configuration import Configuration
import os


class Sbd(object):
    def __init__(self, config=None):
        printCustom("Create instance of sbd", STDOUT_TYPE.INFO)

        if (config == None):
            printCustom("You have to specify a valid configuration instance!", STDOUT_TYPE.ERROR)

        # load configurations specified in core config file
        self.__core_config = config
        self.__sbd_config_file = self.__core_config.sbd_config_file
        self.__video_download_path = self.__core_config.video_download_path

        # initialize sbd plugin
        self.__sbd_instance = SBD(self.__sbd_config_file)

    def run(self, video_instance_list=None):
        printCustom("start sbd process ... ", STDOUT_TYPE.INFO)

        if(video_instance_list == None):
            printCustom("You have to specify a valid non-empty list of video objects (class-type: Video)",
                        STDOUT_TYPE.ERROR)
            exit()

        for video_instance in video_instance_list:
            video_instance.printInfo()

            video_filename = os.path.join(video_instance.download_path + video_instance.file_name)
            self.__sbd_instance.runOnSingleVideo(video_filename=video_filename,
                                                 max_recall_id=video_instance.id)

        printCustom("sbd process finished!", STDOUT_TYPE.INFO)

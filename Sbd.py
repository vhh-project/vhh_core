from vhh_sbd.SBD import SBD
from vhh_sbd.utils import *
import os


class Sbd(object):
    """
    This class includes the interfaces and methods to use the plugin package SBD.
    """

    def __init__(self, config=None):
        """
        Constructor

        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """
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
        """
        This method is used to run the shot boundary detection task

        :param video_instance_list: parameter must hold a list of video objects (Class-type: Video)
        """
        printCustom("start sbd process ... ", STDOUT_TYPE.INFO)

        if(video_instance_list == None):
            printCustom("You have to specify a valid non-empty list of video objects (class-type: Video)",
                        STDOUT_TYPE.ERROR)
            exit()

        for video_instance in video_instance_list:
            video_instance.printInfo()
            video_filename = os.path.join(video_instance.download_path,
                                          str(video_instance.id)) + "." + video_instance.video_format
            #print(video_filename)
            self.__sbd_instance.runOnSingleVideo(video_filename=video_filename,
                                                 max_recall_id=video_instance.id)

        printCustom("sbd process finished!", STDOUT_TYPE.INFO)

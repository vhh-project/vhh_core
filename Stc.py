from vhh_stc.STC import STC
from vhh_stc.utils import *
import os
import yaml


class Stc(object):
    """
    This class includes the interfaces and methods to use the plugin package STC.
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
        self.__stc_config_file = self.__core_config.stc_config_file
        self.__sbd_config_file = self.__core_config.sbd_config_file
        self.__video_download_path = self.__core_config.video_download_path

        # initialize sbd plugin
        self.__stc_instance = STC(self.__stc_config_file)

        fp = open(self.__core_config.sbd_config_file, 'r')
        sbd_config = yaml.load(fp, Loader=yaml.BaseLoader)
        self.__sbd_results_dir = sbd_config['SbdCore']['PATH_FINAL_RESULTS']
        fp.close()

    def get_results_directory(self):
        return self.__stc_instance.config_instance.path_final_results

    def run(self, video_instance_list=None):
        """
        This method is used to run the shot type classification task.
        
        :param video_instance_list: parameter must hold a list of video objects (Class-type: Video)
        """

        printCustom("start stc process ... ", STDOUT_TYPE.INFO)
        print("STC ON", video_instance_list)

        for video_instance in video_instance_list:
            video_instance.printInfo()
            vid = str(video_instance.id)
            print("STC ", vid)
            sbd_results_file = os.path.join(self.__sbd_results_dir, vid + ".csv")           
            shots_np = self.__stc_instance.loadSbdResults(sbd_results_file)
            self.__stc_instance.runOnSingleVideo(shots_per_vid_np=shots_np, max_recall_id=vid)

        printCustom("stc process finished!", STDOUT_TYPE.INFO)

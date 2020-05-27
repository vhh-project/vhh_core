from cmc.CMC import CMC
import os
import yaml


class Cmc(object):
    """
    This class includes the interfaces and methods to use the plugin package CMC.
    """

    def __init__(self, config=None):
        """
        Constructor

        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """

        print("Create instance of cmc")

        if (config == None):
            print("You have to specify a valid configuration instance!")

        # load configurations specified in core config file
        self.__core_config = config
        self.__cmc_config_file = self.__core_config.cmc_config_file
        self.__sbd_config_file = self.__core_config.sbd_config_file
        self.__video_download_path = self.__core_config.video_download_path

        # initialize sbd plugin
        self.__cmc_instance = CMC(self.__cmc_config_file)

        fp = open(self.__core_config.sbd_config_file, 'r')
        sbd_config = yaml.load(fp, Loader=yaml.BaseLoader)
        self.__sbd_results_dir = sbd_config['SbdCore']['PATH_FINAL_RESULTS']
        fp.close()

    def run(self):
        """
        This method is used to run the camera movements classification task.
        """

        print("start cmc process ... ")

        results_file_list = os.listdir(self.__sbd_results_dir)
        for file in results_file_list:
            vid = int(file.split('.')[0])
            shots_np = self.__cmc_instance.loadSbdResults(self.__sbd_results_dir + file)
            self.__cmc_instance.runOnSingleVideo(shots_per_vid_np=shots_np, max_recall_id=vid)

        print("cmc process finished!")

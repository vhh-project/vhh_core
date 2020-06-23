from Sbd import Sbd
from Stc import Stc
from Cmc import Cmc
from VhhRestApi import VhhRestApi
from Configuration import Configuration
import numpy as np
import os


class MainController(object):
    """
    This class represents the Main part of this application and includes all interfaces and methods to use the automatic annotation plugins.
    """

    def __init__(self):
        """
        Constructor
        """
        print("Create instance of MainController")

        # load CORE configuration
        config_file = "/home/dhelm/VHH_Develop/pycharm_vhh_core/config/CORE/config.yaml"
        self.__configuration_instance = Configuration(config_file=config_file)
        self.__configuration_instance.loadConfig()

        self.__root_url = self.__configuration_instance.root_url
        self.__pem_path = self.__configuration_instance.pem_path
        self.__video_download_path = self.__configuration_instance.video_download_path

        self.__sbd_config_file = self.__configuration_instance.sbd_config_file
        self.__stc_config_file = self.__configuration_instance.stc_config_file
        self.__cmc_config_file = self.__configuration_instance.cmc_config_file

        # initialize class members
        self.__sbd_instance = Sbd(config=self.__configuration_instance)
        self.__stc_instance = Stc(config=self.__configuration_instance)
        self.__cmc_instance = Cmc(config=self.__configuration_instance)

        self.__rest_api_instance = VhhRestApi(config=self.__configuration_instance)

    def run(self):
        """
        This method is used to start the automatic annotation process.
        """

        print("Start automatic annotation process ... ")

        # get list of videos in mmsi
        video_instance_list = self.__rest_api_instance.getListofVideos()
        #video_instance_list = video_instance_list[1:]

        # cleanup video and results folder
        if (self.__configuration_instance.cleanup_flag == 1):
            for video_instance in video_instance_list:
                video_instance.cleanup()

        # download videos if not available
        for video_instance in video_instance_list:
            if (video_instance.is_downloaded() == False):
                video_instance.download(self.__rest_api_instance)

        # run sbd
        self.__sbd_instance.run(video_instance_list=video_instance_list)

        # run stc
        self.__stc_instance.run()

        # run cmc
        self.__cmc_instance.run()

        # merge all results
        results_np = self.merge_results()

        # post all results
        vids = np.unique(results_np[:, 1:2])
        for vid in vids:
            indices = np.where(vid == results_np[:, 1:2])[0]
            vid_results_np = results_np[indices]

            header = ["shot_id", "vid_name", "start", "end", "stc", "cmc"]
            header_np = np.expand_dims(np.array(header), axis=0)
            vid_results_np = np.concatenate((header_np, vid_results_np), axis=0)

            self.__rest_api_instance.postAutomaticResults(vid=int(vid.split('.')[0]), results_np=vid_results_np)

        print("Successfully finished!")

    def merge_results(self):
        """
        This method is used to merge and prepare the results of each individual plugin (sbd, stc, cmc) to send it to the the Vhh-MMSI database.

        :return: This method returns a numpy array holding all results (including a valid header).
        """
        # merge and prepare results
        sbd_results_path = os.path.join(self.__configuration_instance.results_root_dir, "sbd")
        sbd_results_path = os.path.join(sbd_results_path, "final_results")

        stc_results_path = os.path.join(self.__configuration_instance.results_root_dir, "stc")
        stc_results_path = os.path.join(stc_results_path, "final_results")

        cmc_results_path = os.path.join(self.__configuration_instance.results_root_dir, "cmc")
        cmc_results_path = os.path.join(cmc_results_path, "final_results")

        sbd_result_file_list = os.listdir(sbd_results_path)
        sbd_result_file_list = [os.path.join(sbd_results_path, x) for x in sbd_result_file_list]
        stc_result_file_list = os.listdir(stc_results_path)
        stc_result_file_list = [os.path.join(stc_results_path, x) for x in stc_result_file_list]
        cmc_result_file_list = os.listdir(cmc_results_path)
        cmc_result_file_list = [os.path.join(cmc_results_path, x) for x in cmc_result_file_list]

        print(sbd_result_file_list)
        print(stc_result_file_list)
        print(cmc_result_file_list)

        entries = []
        for results_file in sbd_result_file_list:
            fp = open(results_file)
            lines = fp.readlines()
            fp.close()

            for line in lines[1:]:
                line = line.replace('\n', '')
                line_split = line.split(';')
                entries.append([line_split[0].split('.')[0],
                                line_split[1],
                                line_split[2],
                                line_split[3]])
        sbd_entries_np = np.array(entries)

        entries = []
        for results_file in stc_result_file_list:
            fp = open(results_file)
            lines = fp.readlines()
            fp.close()

            for line in lines[1:]:
                line = line.replace('\n', '')
                line_split = line.split(';')
                entries.append([line_split[0].split('.')[0],
                                line_split[1],
                                line_split[2],
                                line_split[3],
                                line_split[4]])
        stc_entries_np = np.array(entries)

        entries = []
        for results_file in cmc_result_file_list:
            fp = open(results_file)
            lines = fp.readlines()
            fp.close()

            for line in lines[1:]:
                line = line.replace('\n', '')
                line_split = line.split(';')
                entries.append([line_split[0].split('.')[0],
                                line_split[1],
                                line_split[2],
                                line_split[3],
                                line_split[4]])
        cmc_entries_np = np.array(entries)

        if(len(stc_entries_np) > 0 and len(cmc_entries_np) > 0):
            entries_np = np.concatenate((sbd_entries_np, stc_entries_np[:, 4:]), axis=1)
            entries_np = np.concatenate((entries_np, cmc_entries_np[:, 4:]), axis=1)
        else:
            dummy_entries_np = np.empty([len(sbd_entries_np), 1]).astype('str')
            dummy_entries_np[:] = "NA"
            entries_np = np.concatenate((sbd_entries_np, dummy_entries_np), axis=1)
            entries_np = np.concatenate((entries_np, dummy_entries_np), axis=1)

        return entries_np


    '''
    def run_stc_process(self, sbd_results_path, config_file):
        print("start stc process ... ")

        # initialize and run stc process
        stc_instance = STC(config_file)

        results_file_list = os.listdir(sbd_results_path)
        print(results_file_list)

        for file in results_file_list:
            vid = int(file.split('.')[0])
            shots_np = stc_instance.loadSbdResults(sbd_results_path + file)
            stc_instance.runOnSingleVideo(shots_per_vid_np=shots_np, max_recall_id=vid)

        printCustom("stc process finished!", STDOUT_TYPE.INFO)

    def run_download_process(self, rest_api_instance, video_instance_list):
        print("start download process ... ")
        for video_instance in video_instance_list:
            video_instance.printInfo()
            rest_api_instance.downloadVideo(video_instance.url,
                                            video_instance.originalFileName,
                                            video_instance.video_format)
        print("download process finished ... ")
    '''

    '''
    # load configuration
    config_file = "/home/dhelm/VHH_Develop/pycharm_vhh_core/config/CORE/config.yaml"
    configuration_instance = Configuration(config_file=config_file)

    root_url = configuration_instance.root_url
    pem_path = configuration_instance.pem_path
    video_download_path = configuration_instance.video_download_path
    sbd_config_file = configuration_instance.sbd_config_file
    stc_config_file = configuration_instance.stc_config_file
    cmc_config_file = configuration_instance.cmc_config_file

    # create rest api instance
    rest_api_instance = VhhRestApi(root_url=root_url, pem_path=pem_path, video_download_path=video_download_path)

    if (configuration_instance.debug_flag == 0):
        ACTIVATE_GET_VID_LIST_FLAG = True
        ACTIVATE_DOWNLOAD_FLAG = True
        ACTIVATE_SBD_FLAG = True
        ACTIVATE_STC_FLAG = True
        ACTIVATE_CMC_FLAG = False
        ACTIVATE_GET_AUTO_RESULTS_FLAG = False
        ACTIVATE_POST_AUTO_RESULTS_FLAG = True
    else:
        ACTIVATE_GET_VID_LIST_FLAG = False
        ACTIVATE_DOWNLOAD_FLAG = False
        ACTIVATE_SBD_FLAG = False
        ACTIVATE_STC_FLAG = False
        ACTIVATE_CMC_FLAG = False
        ACTIVATE_GET_AUTO_RESULTS_FLAG = False
        ACTIVATE_POST_AUTO_RESULTS_FLAG = False



    # ##########################
    # get film list with urls
    video_instance_list = rest_api_instance.getListofVideos()


    if (ACTIVATE_DOWNLOAD_FLAG == True):
        # ##########################
        # download all videos
        run_download_process(rest_api_instance, video_instance_list)

    if (ACTIVATE_SBD_FLAG == True):
        # ##########################
        # run sbd

        for video_instance in video_instance_list:
            video_instance.printInfo()
            run_sbd_process(video_path=video_instance.download_path,
                            file_name=video_instance.originalFileName + "." + video_instance.video_format,
                            vid=video_instance.id,
                            config_file=sbd_config_file)

    if (ACTIVATE_STC_FLAG == True):
        # ##########################
        # run stc

        sbd_final_results_path = "/data/share/maxrecall_vhh_mmsi/videos/results/sbd/final_results/"
        run_stc_process(sbd_results_path=sbd_final_results_path,
                        config_file=stc_config_file
                        )

    if (ACTIVATE_CMC_FLAG == True):
        # ##########################
        # run cmc
        print("NOT_IMPLEMENTED YET")

    if (ACTIVATE_POST_AUTO_RESULTS_FLAG == True):
        # ##########################
        # post all results

        # ##########################
        # prepare results and send it to maxrecall

        results_path = "/data/share/maxrecall_vhh_mmsi/videos/results/stc/final_results/"
        result_file_list = os.listdir(results_path)
        print(result_file_list)

        fp = open(results_path + "/" + result_file_list[1])
        lines = fp.readlines()
        fp.close()

        print(lines)
        entries = []
        for line in lines:
            line = line.replace('\n', '')
            line_split = line.split(';')
            entries.append([line_split[0], line_split[1], line_split[2], line_split[3], line_split[4]])
        entries_np = np.array(entries)
        print(entries_np)

        rest_api_instance.postAutomaticResults(vid=10, results_np=entries_np)

    if (ACTIVATE_GET_AUTO_RESULTS_FLAG == True):
        # ##########################
        # get all results
        rest_api_instance.getAutomaticResults(vid=10)
    '''

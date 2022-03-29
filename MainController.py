from Sbd import Sbd
from Stc import Stc
from Cmc import Cmc
from Odt import Odt
from VhhRestApi import VhhRestApi
from Configuration import Configuration
import numpy as np
import os
import csv
import json
import urllib
import zipfile


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
        config_file = "config/CORE/config.yaml"
        self.__configuration_instance = Configuration(config_file=config_file)
        self.__configuration_instance.loadConfig()

        if self.make_model_folders():
            print("Models have been downloaded.")

        self.__root_url = self.__configuration_instance.root_url
        self.__pem_path = self.__configuration_instance.pem_path
        self.__video_download_path = self.__configuration_instance.video_download_path

        self.__sbd_config_file = self.__configuration_instance.sbd_config_file
        self.__stc_config_file = self.__configuration_instance.stc_config_file
        self.__cmc_config_file = self.__configuration_instance.cmc_config_file
        self.__odt_config_file = self.__configuration_instance.odt_config_file

        # initialize class members
        self.__sbd_instance = Sbd(config=self.__configuration_instance)
        self.__stc_instance = Stc(config=self.__configuration_instance)
        self.__cmc_instance = Cmc(config=self.__configuration_instance)
        self.__odt_instance = Odt(config=self.__configuration_instance)

        self.__rest_api_instance = VhhRestApi(
            config=self.__configuration_instance, main_controller=self)

        path_core_results = os.path.join(
            self.__configuration_instance.results_root_dir, "core")
        self.__path_sba, self.__path_oba = os.path.join(
            path_core_results, "SBA"), os.path.join(path_core_results, "OBA")
        self.__path_tba = os.path.join(path_core_results, "TBA")

        self.make_video_folder()
        self.make_result_folders()

    def get_rest_api(self):
        """
        Allows access to the REST API
        """
        return self.__rest_api_instance

    def get_config(self):
        return self.__configuration_instance

    def run(self):
        """
        This method is used to start the automatic annotation process.
        """

        print("Start automatic annotation process ... ")

        # get list of videos in mmsi
        video_instance_list = self.__rest_api_instance.getListofVideos()
        # video_instance_list = video_instance_list[0:2]

        # cleanup coplete results and video folder
        if (self.__configuration_instance.cleanup_flag == 1):
            print("Cleaning up")
            for video_instance in video_instance_list:
                video_instance.cleanup()

        #
        # COLLECT VIDEOS
        #

        videos_to_process = []
        for i, video_instance in enumerate(video_instance_list):
            # For now we only care for shot, camera_movements and object detection
            if (not video_instance.processed_flags["shots"]) or (not video_instance.processed_flags["camera_movements"]) or (not video_instance.processed_flags["objects"]):
                videos_to_process.append(video_instance)

        if(len(videos_to_process) == 0):
            print("All videos are already processed!")
            exit()
        else:
            print("Found {0} videos to process".format(len(videos_to_process)))


        print("-------------------------------------------------------------------")
        print("------------------ BATCH PROCESSING -------------------------------")
        batch_size = self.__configuration_instance.batch_size

        for i in range(0, len(videos_to_process), batch_size):
            start_pos = i
            end_pos = i + batch_size
            batch_video_instance_list = videos_to_process[start_pos:end_pos]

            for video_instance in batch_video_instance_list:
                video_instance.printInfo()

            # cleanup video and results folder
            if (self.__configuration_instance.cleanup_flag == 1):
                print("Cleaning up")
                for video_instance in video_instance_list:
                    video_instance.cleanup()

            #
            # DOWNLOAD VIDEOS
            #

            # download if not available
            for video_instance in batch_video_instance_list:
                if (video_instance.is_downloaded() == False):
                    ret = video_instance.download(self.__rest_api_instance)

                    # if for some reason it is not possible to download the video than skip it
                    print(ret)
                    if(ret == False):
                        print(
                            "Not able to download this video! e.g. access restrictions or missing video file! --> skip")
                        continue

            #
            # RUN THE PIPELINE
            #
            print("Run pipeline on a batch")

            # run sbd & stc
            videos_to_process_shots = list(
                filter(lambda x: not x.processed_flags["shots"], batch_video_instance_list))
            videos_to_download_shots = list(
                filter(lambda x: x.processed_flags["shots"], batch_video_instance_list))

            if self.__configuration_instance.use_sbd:
                self.__sbd_instance.run(
                    video_instance_list=videos_to_process_shots)

            if self.__configuration_instance.use_stc:
                self.__stc_instance.run(
                    video_instance_list=videos_to_process_shots)

            # Download shot info (SBD, STC) for already processed videos
            for video_instance in videos_to_download_shots:
                self.__rest_api_instance.getShotResults(vid=video_instance.id)

            # run cmc
            videos_to_process_cmc = list(filter(
                lambda x: not x.processed_flags["camera_movements"], batch_video_instance_list))
            videos_to_download_cmc = list(filter(
                lambda x: x.processed_flags["camera_movements"], batch_video_instance_list))

            if self.__configuration_instance.use_cmc:
                self.__cmc_instance.run(
                    video_instance_list=videos_to_process_cmc)

            # TODO: Download camera movements data for videos that are already processed

            # run odt
            videos_to_process_objects = list(
                filter(lambda x: not x.processed_flags["objects"], batch_video_instance_list))
            videos_to_download_objects = list(
                filter(lambda x: x.processed_flags["objects"], batch_video_instance_list))

            if self.__configuration_instance.use_odt:
                self.__odt_instance.run(
                    video_instance_list=videos_to_process_objects)

            # TODO: Download object detection data for videos that are already processed

            #
            # CORRECT FORMAT + POST TO VHH MMSI
            #

            if len(videos_to_process_shots) > 0:
                results_sba = self.merge_results_SBA(videos_to_process_shots)
                sba_paths = self.store_SBA_results(results_sba)

                if self.__configuration_instance.do_send_to_server:
                    self.__rest_api_instance.postSBAResults(sba_paths)

            if len(videos_to_process_cmc) > 0:
                results_tba = self.format_results_TBA(videos_to_process_cmc)
                tba_paths = self.store_TBA_results(results_tba)

                if self.__configuration_instance.do_send_to_server:
                    self.__rest_api_instance.postTBAResults(tba_paths)

            if len(videos_to_process_objects) > 0:
                results_oba = self.format_results_OBA(
                    videos_to_process_objects)
                oba_paths = self.store_OBA_results(results_oba)

                if self.__configuration_instance.do_send_to_server:
                    self.__rest_api_instance.postOBAResults(oba_paths)

        print("Successfully finished!")

    def store_OBA_results(self, results_oba):
        """
        Stores the OBA results in JSON files so they are ready to be sent to VHH-MMSI

        :param results_oba: Output of merge_results_OBA
        """
        paths = []
        for dict in results_oba:
            json_path = os.path.join(
                self.__path_oba, str(dict["videoId"]) + ".json")
            paths.append(json_path)
            with open(json_path, 'w', newline='') as json_file:
                json.dump(dict['objects'], json_file)
        return paths

    def store_SBA_results(self, results_sba):
        """
        Stores the SBA results in JSON files so they are ready to be sent to VHH-MMSI

        :param results_sba: Output of merge_results_sba
        """
        paths = []
        vids = np.unique(results_sba[:, :1])

        for vid in vids:
            indices = np.where(vid == results_sba[:, 0])[0]
            vid_results_sba = results_sba[indices]
            shots = []
            rows, _ = vid_results_sba.shape

            for row_idx in range(rows):
                shot = {
                    "inPoint": int(vid_results_sba[row_idx, 2])+1,
                    "outPoint": int(vid_results_sba[row_idx, 3])+1,
                    "shotType": vid_results_sba[row_idx, 4]
                    # "cameraMovement": vid_results_sba[row_idx, 5]
                }
                shots.append(shot)

            # Write shots to JSON file
            json_path = os.path.join(self.__path_sba, str(vid) + ".json")
            paths.append(json_path)
            with open(json_path, 'w', newline='') as json_file:
                json.dump(shots, json_file)
        return paths

    def store_TBA_results(self, results_tba):
        """
        Stores the TBA results in JSON files so they are ready to be sent to VHH-MMSI

        :param results_tba: Output of merge_results_TBA
        """
        paths = []
        for dict in results_tba:
            json_path = os.path.join(
                self.__path_tba, str(dict["videoId"]) + ".json")
            paths.append(json_path)
            with open(json_path, 'w', newline='') as json_file:
                json.dump(dict['camera_movements'], json_file)
        return paths

    def merge_results_SBA(self, relevant_videos):
        """
        This method is used to merge and prepare the results of shot based annotation data (sbd, stc, cmc) to send it to the the Vhh-MMSI database.

        :return: This method returns a numpy array holding sbd, stc, cmc results (including a valid header).
        """

        relevant_files = [str(video.id) + ".csv" for video in relevant_videos]
        # merge and prepare results
        sbd_results_path = os.path.join(
            self.__configuration_instance.results_root_dir, "sbd")
        sbd_results_path = os.path.join(sbd_results_path, "final_results")
        stc_results_path = os.path.join(
            self.__configuration_instance.results_root_dir, "stc")
        stc_results_path = os.path.join(stc_results_path, "final_results")

        #cmc_results_path = os.path.join(self.__configuration_instance.results_root_dir, "cmc")
        #cmc_results_path = os.path.join(cmc_results_path, "final_results")

        sbd_result_file_list = os.listdir(sbd_results_path)
        sbd_result_file_list = [os.path.join(
            sbd_results_path, x) for x in sbd_result_file_list if x in relevant_files]
        stc_result_file_list = os.listdir(stc_results_path)
        stc_result_file_list = [os.path.join(
            stc_results_path, x) for x in stc_result_file_list if x in relevant_files]
        #cmc_result_file_list = os.listdir(cmc_results_path)
        #cmc_result_file_list = [os.path.join(cmc_results_path, x) for x in cmc_result_file_list if x in relevant_files]

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
        print(sbd_entries_np)

        entries = []
        for results_file in stc_result_file_list:
            fp = open(results_file)
            lines = fp.readlines()
            fp.close()

            for line in lines[1:]:
                line = line.replace('\n', '')
                line_split = line.split(';')

                # TODO: just a temporary workaround
                # if (line_split[4] == 'I'):
                #    line_split[4] = 'NA'
                entries.append([line_split[0].split('.')[0],
                                line_split[1],
                                line_split[2],
                                line_split[3],
                                line_split[4]])
        stc_entries_np = np.array(entries)
        print(stc_entries_np)

        '''
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
        print(cmc_entries_np)
        '''

        if(len(stc_entries_np) > 0):
            entries_np = np.concatenate(
                (sbd_entries_np, stc_entries_np[:, 4:]), axis=1)
        else:
            dummy_entries_np = np.empty([len(sbd_entries_np), 1]).astype('str')
            dummy_entries_np[:] = "NA"
            entries_np = np.concatenate(
                (sbd_entries_np, dummy_entries_np), axis=1)
        print(entries_np)
        return entries_np

    def format_results_TBA(self, relevant_videos):
        """
        This method is used to merge and prepare the results of time-based annotation data (cmc) to send it to the the Vhh-MMSI database.

        :return: This method returns a list of dictionaries, each containing the CMC result of one single video.
        """
        relevant_files = [str(video.id) + ".json" for video in relevant_videos]

        cmc_results_path = os.path.join(
            self.__configuration_instance.results_root_dir, "cmc")
        cmc_results_path = os.path.join(cmc_results_path, "final_results")

        cmc_result_file_list = [os.path.join(cmc_results_path, x) for x in os.listdir(
            cmc_results_path) if x in relevant_files]
        video_dicts = []
        for file_path in cmc_result_file_list:
            videoId = file_path.split('/')[-1]
            videoId = videoId.split('.')[0]
            with open(file_path, mode='r') as json_file:
                data = json.load(json_file)

                results = []
                for data_entry in data:
                    inpoint = int(data_entry['start']) + 1
                    outpoint = int(data_entry['stop']) + 1
                    camera_movement = data_entry['cmcType']

                    result_entry = {
                        "inPoint": inpoint,
                        "outPoint": outpoint,
                        "cameraMovement": camera_movement
                    }
                    results.append(result_entry)

                # Objects need to be stored in a list and not a dict
                video_dict = {"videoId": videoId, "camera_movements": results}
            video_dicts.append(video_dict)

        return video_dicts

    def format_results_OBA(self, relevant_videos):
        """
        This method is used to merge and prepare the results of object based annotation data (od) to send it to the the Vhh-MMSI database.

        :return: This method returns a list of dictionaries, each containing the ODT result of one single video.
        """
        relevant_files = [str(video.id) + ".csv" for video in relevant_videos]

        od_results_path = os.path.join(
            self.__configuration_instance.results_root_dir, "od")
        od_results_path = os.path.join(od_results_path, "final_results")

        od_result_file_list = [os.path.join(od_results_path, x) for x in os.listdir(
            od_results_path) if x in relevant_files]
        video_dicts = []
        for file_path in od_result_file_list:
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)

                objects_dict = {}
                videoId = None

                for row in csv_reader:
                    # Get videoId, this requires the moviename to have the form videoId.fileending e.g. "8213.m4v"
                    if videoId is None:
                        videoId = int(row["movie_name"].split(".")[0])

                    bb = {"fid": int(row["fid"]) + 1,
                          "cbb": -1,
                          "coc": -1,
                          "x1": float(row["bb_x1"]),
                          "x2": float(row["bb_x2"]),
                          "y1": float(row["bb_y1"]),
                          "y2": float(row["bb_y2"])}

                    # Store bounding box
                    if row["oid"] in objects_dict:
                        objects_dict[row["oid"]]["bbs"].append(bb)
                    else:
                        obj = {"bbs": [bb],
                               "className": row["class_name"],
                               "id": int(row["oid"]),
                               "inPoint": int(row["start"]) + 1,
                               "outPoint": int(row["stop"]) + 1,
                               "valueSource": "TUW CV Object Detection (v0.1)"}
                        objects_dict[row["oid"]] = obj

                # Objects need to be stored in a list and not a dict
                video_dict = {"videoId": videoId,
                              "objects": list(objects_dict.values())}
            video_dicts.append(video_dict)
        return video_dicts

    def make_result_folders(self):

        results_root_dir = self.__configuration_instance.results_root_dir
        plugins = ["sbd", "stc", "cmc", "od"]
        results_sub_dirs = ["raw_results", "final_results", "develop"]

        try:
            os.mkdir(results_root_dir)
        except OSError:
            pass

        for plugin in plugins:
            for sub_dir in results_sub_dirs:
                try:
                    os.makedirs(os.path.join(
                        results_root_dir, plugin, sub_dir))
                except OSError:
                    pass

        try:
            os.mkdir(os.path.join(results_root_dir, "core"))
        except OSError:
            pass

        results_types = ["TBA", "OBA", "SBA"]
        path = os.path.join(results_root_dir, "core")
        for type in results_types:
            try:
                os.mkdir(os.path.join(path, type))
            except OSError:
                pass

    def make_video_folder(self):
        video_root_dir = self.__configuration_instance.video_download_path
        try:
            os.mkdir(video_root_dir)
        except OSError:
            pass

    def make_model_folders(self):
        """
        If the "models" folder does not exist, create the folder and download the models into it
        """
        model_root_dir = self.__configuration_instance.model_path

        try:
            os.mkdir(model_root_dir)
        except OSError:
            return False
        print("Created models folder")

        url = 'https://zenodo.org/record/5704641/files/vhh_models.zip?download=1'
        path = "models.zip"

        print("Downloading models")
        try:
            urllib.request.urlretrieve(url, path)
        except (urllib.error.URLError, IOError) as e:
            print("Downloading failed:\n", e)
            print("Deleting models folder")
            os.rmdir(model_root_dir)

        print("Unzipping models")
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(model_root_dir)

        print("Removing zipped models")
        os.remove(path)

        return True

    def get_result_directory(self, component):
        if component == "SBD":
            return self.__sbd_instance.get_results_directory()
        elif component == "STC":
            return self.__stc_instance.get_results_directory()
        elif component == "CMC":
            return self.__cmc_instance.get_results_directory()
        else:
            raise ValueError("Unknown component")

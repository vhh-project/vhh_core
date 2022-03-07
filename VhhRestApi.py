import json
import requests
import os
import csv
from Video import Video
import urllib.parse

class VhhRestApi(object):
    """
    This class includes the interfaces and methods to use the vhh restAPI interfaces provided by MaxRecall.
    """

    def __init__(self, config=None, main_controller=None):
        """
        Constructor

        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """

        print("create instance of VhhRestApi ...")

        if (config == None):
            print("You have to specify a valid configuration instance!")

        # load configurations specified in core config file
        self.__core_config = config
        self.__pem_path = self.__core_config.pem_path
        self.__root_url = self.__core_config.root_url
        self.__video_download_path = self.__core_config.video_download_path

        # create urls
        self.API_VIDEO_SEARCH_ENDPOINT = urllib.parse.urljoin(self.__root_url, "videos/search")
        self.API_VIDEO_SHOTS_AUTO_ENDPOINT = urllib.parse.urljoin(self.__root_url, "videos/")  # 8/shots/auto

        self.main_controller = main_controller

    def getRequest(self, url):
        """
        This method is used to send a get request to the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :return: This method returns the original response including header as well as payload.
        """
        print("send get request: " + str(url))
        response = requests.get(url) #,verify=self.__pem_path)  # params=params,
        print("receive get response:", response)
        return response

    def postRequest(self, url, data_dict):
        """
        This method is used to send a post request to the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :param data_dict: this parameter must hold a valid list of dictionaries with the specified fields (see RestApi documentation).
        :return: This method returns the original response including header as well as payload
        """		
        headers = {
                    'accept': '*/*',
                    'Content-Type': 'application/json',
                  }

        payload = json.dumps(data_dict)
        print("send post request: " + str(url))
        response = requests.post(url=url, headers=headers, data=payload)#, verify=self.__pem_path)  # , header=headers
        print("receive post response")
        return response

    def getListofVideos(self):
        """
        This method is used to get a list of all available videos in the VHH-MMSI system.

        :return: This method returns a list of video objects (Class-type: Video) which holds all video specific meta-data.
        """
        print("load list of videos ... ")

        print("send request: " + str(self.API_VIDEO_SEARCH_ENDPOINT))

        # payload = {"tuwcvProcessedObjects": False, "tuwcvProcessedOverscan": False, "tuwcvProcessedRelations": False, "tuwcvProcessedShots": False}
        res = requests.get(self.API_VIDEO_SEARCH_ENDPOINT, params={}) #, verify=self.__pem_path)  # params=params,
        print("receive response: ", res)
        res_json = res.json()

        video_instance_list = []

        for i, entry in enumerate(res_json['results']):
            vid = int(entry['id'])
            originalFileName = entry['originalFileName']
            url = entry['url']

            # filter frame_counter videos and amX videos
            if not "video-framecounter" in originalFileName and not "eyeland" in originalFileName and not "am-" in originalFileName:
                video_instance = Video(self.__core_config)
                video_instance.create_video(vid=vid,
                                            originalFileName=originalFileName,
                                            url=url,
                                            download_path=self.__video_download_path,
                                            processed_flag_shots = entry['tuwcvProcessedShots'],
                                            processed_flag_objects = entry['tuwcvProcessedObjects'],
                                            processed_flag_relations = entry['tuwcvProcessedRelations'],
                                            processed_flag_overscan = entry['tuwcvProcessedOverscan'])
                video_instance_list.append(video_instance)

        return video_instance_list

    def getAutomaticResults(self, vid):
        """
        This method is used to get all automatic generated results from the VhhMMSI system.
        :param vid: This parameter must hold a valid video identifier.
        :return: This method returns the results (payload) as json format.
        """
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        response = self.getRequest(url)
        res_json = response.json()
        return res_json

    def getManualResults(self, vid):
        """
        This method is used to get all manually generated results from the VhhMMSI system.
        :param vid: This parameter must hold a valid video identifier.
        :return: This method returns the results (payload) as json format.
        """
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/tbas/shots/manual"
        response = self.getRequest(url)
        res_json = response.json()
        return res_json

    def downloadVideo(self, url, file_name, video_format):
        """
        This method is used to download a video from the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :param file_name: This parameter represents the filename on the local storage.
        :param video_format: This parameter must hold a valid video format extension (e.g. m4v)
        :return: This method returns a boolean flag which includes the state of the download process (true ... sucessfully finished OR false ... downlaod failed)
        """
        ret = False

        try:
            video_file = requests.get(url) #, verify=self.__pem_path)
            open(self.__video_download_path + "/" + file_name + "." + str(video_format), 'wb').write(video_file.content)
            ret = True
        except:
            print("Download process failed!")
            ret = False

        return ret

    def downloadSTCData(self, vid, download_dir):
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/tbas/shots/manual"
        response = self.getRequest(url)
        res_json = response.json()

        file_name = str(vid) + ".csv"
        path = os.path.join(download_dir, file_name)

        with open(path, 'w') as file:
            fieldnames_stc = ["vid_name", "shot_id", "start", "end", "stc"]
            writer_stc = csv.DictWriter(file, fieldnames=fieldnames_stc, delimiter=";")
            writer_stc.writeheader()

            vid_name = str(vid) + ".m4v"
            shot_id_stc = 1

            new_shots = []
            # The JSON does not contain information about shots with NA camera movement, need to add it by finding shots for which no camera movement is given
            for shot in filter(lambda x: 'shotType' in x.keys(), res_json):
                if len(list(filter(lambda x: "cameraMovement" in x.keys() and x["inPoint"] == shot["inPoint"] and x["outPoint"] == shot["outPoint"], res_json))) == 0:
                    new_shots.append({"inPoint": shot["inPoint"], "outPoint": shot["outPoint"], "cameraMovement": "NA"})

            res_json += new_shots  
            # Sort numbers, so the shot ids are correct
            res_json.sort(key=lambda shot: shot["inPoint"])

            for shot in res_json:
                if not 'cameraMovement' in shot.keys():
                    writer_stc.writerow({'vid_name': vid_name, "shot_id": shot_id_stc, "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "stc": shot["shotType"]})
                    shot_id_stc += 1
    
        return

    def getSTCResult(self, vid):
        """
        This method is used to download shot results (STC) from the VhhMMSI system.

        :return: A list of dictionaries that represent the STC file (in a format that can be directly stored as a csv)
        """
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        vid_name = f"{vid}.m4v"
        response = self.getRequest(url)
        res_json = response.json()

        results = []
        shot_id_stc = 1
        for shot in res_json:
            if not 'cameraMovement' in shot.keys():
                results.append({'vid_name': vid_name, "shot_id": shot_id_stc, "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "stc": shot["shotType"]})
                shot_id_stc += 1
        return results

    def getShotResults(self, vid):
        """
        This method is used to download shot results (SBD, STC, CMC) from the VhhMMSI system.

        :param vid: This parameter must hold a valid video identifier.
        """

        print("get sbd results from maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        response = self.getRequest(url)
        res_json = response.json()

        file_name = str(vid) + ".csv"
        sbd_path = os.path.join(self.main_controller.get_result_directory("SBD"), file_name)
        stc_path = os.path.join(self.main_controller.get_result_directory("STC"), file_name)
        cmc_path = os.path.join(self.main_controller.get_result_directory("CMC"), file_name)

        print("stc_path:", stc_path)
        print("cmc_path:", cmc_path)

        with open(sbd_path, 'w') as sbd_file:
            with open(stc_path, 'w') as stc_file:
                with open(cmc_path, 'w') as cmc_file:

                    fieldnames_sbd = ["vid_name", "shot_id", "start", "end"]
                    fieldnames_stc = ["vid_name", "shot_id", "start", "end", "stc"]
                    fieldnames_cmc = ["vid_name", "shot_id", "start", "end", "cmc"]

                    writer_sbd = csv.DictWriter(sbd_file, fieldnames=fieldnames_sbd, delimiter=";")
                    writer_stc = csv.DictWriter(stc_file, fieldnames=fieldnames_stc, delimiter=";")
                    writer_cmc = csv.DictWriter(cmc_file, fieldnames=fieldnames_cmc, delimiter=";")

                    writer_sbd.writeheader()
                    writer_stc.writeheader()
                    writer_cmc.writeheader() 

                    vid_name = str(vid) + ".m4v"
                    shot_id_stc = 1
                    shot_id_cmc = 1

                    new_shots = []
                    # The JSON does not contain information about shots with NA camera movement, need to add it by finding shots for which no camera movement is given
                    for shot in filter(lambda x: 'shotType' in x.keys(), res_json):
                        if len(list(filter(lambda x: "cameraMovement" in x.keys() and x["inPoint"] == shot["inPoint"] and x["outPoint"] == shot["outPoint"], res_json))) == 0:
                            new_shots.append({"inPoint": shot["inPoint"], "outPoint": shot["outPoint"], "cameraMovement": "NA"})

                    res_json += new_shots  
                    # Sort numbers, so the shot ids are correct
                    res_json.sort(key=lambda shot: shot["inPoint"])

                    for shot in res_json:
                        if 'cameraMovement' in shot.keys():
                            writer_cmc.writerow({'vid_name': vid_name, "shot_id": shot_id_cmc, "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "cmc": shot["cameraMovement"]})
                            shot_id_cmc += 1
                        else:
                            writer_sbd.writerow({'vid_name': vid_name, "shot_id": shot_id_stc, "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1})
                            writer_stc.writerow({'vid_name': vid_name, "shot_id": shot_id_stc, "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "stc": shot["shotType"]})
                            shot_id_stc += 1
        
        return

    def postAutomaticResults(self, vid, results_np):
        """
        This method is used to post the automatic generated results to the VhhMMSI system.

        :param vid: This parameter must hold a valid video identifier.
        :param results_np: This parameter must hold a numpy array including the automatic generated results.
        """

        print("save all automatic generated results to maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + "/" + str(vid) + "/shots/auto"
        data_block = results_np[1:, :]

        data_dict_l = []
        for i in range(0, len(data_block)):
            print(data_block[i])
            inpoint = int(data_block[i][2]) + 1
            outpoint = int(data_block[i][3]) + 1
            shot_type = data_block[i][4]
            camera_movement = data_block[i][5]

            data_dict = {
                "inPoint": inpoint,
                "outPoint": outpoint,
                "shotType": shot_type,
                "cameraMovement": camera_movement
            }

            data_dict_l.append(data_dict)

        response = self.postRequest(url, data_dict_l)
        print(response)

        print("sbd results successfully sent to maxrecall ... ")

    def postSBAResults(self, sba_paths):
        """
        Posts the automatically generated SBA results (SBD, STC, CMC) to the VhhMMSI system.

        :data: list of paths to json files that contain the shot information
        """
        for path in sba_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = urllib.parse.urljoin(self.API_VIDEO_SHOTS_AUTO_ENDPOINT, "{0}/shots/auto".format(vid))
            with open(path) as file:
                data = json.load(file)
                response = self.postRequest(url, data)
                print(url, ": ", response)

    def postOBAResults(self, oba_paths):
        """
        Posts the automatically generated OBA results (ODT) to the VhhMMSI system.

        :data: list of paths to json files that contain the object information
        """
        for path in oba_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = urllib.parse.urljoin(self.API_VIDEO_SHOTS_AUTO_ENDPOINT, "{0}/objects/auto".format(vid))
            with open(path) as file:
                data = json.load(file)
                response = self.postRequest(url, data)
                print(url, ": ", response)

    def postOSDresults(self, osd_list):
        """
        Posts overscan detections to VhhMMSI

        :osd_list: a list contatining a dictionary for each film
                    The dictionary contains the VID, and the overscan coordinates (left, right, top, bottom) normalized to to the intervall [0, 1]
        """
        for dict in osd_list:
            url = urllib.parse.urljoin(self.API_VIDEO_SHOTS_AUTO_ENDPOINT, "{0}/overscan/auto".format(dict["vid"]))
            response = self.postRequest(url, {
                "left": dict["left"],
                "right": dict["right"],
                "top": dict["top"],
                "bottom": dict["bottom"]
            })
            print(url, ": ", response)

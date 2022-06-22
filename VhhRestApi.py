import json
import requests
import os
import csv
from Video import Video
import urllib.parse
import sys

from RestURLProvider import RestURLProvider

class VhhRestApi(object):
    """
    This class includes the interfaces and methods to use the vhh restAPI interfaces provided by MaxRecall.
    """

    def __init__(self, config, main_controller=None):
        """
        Constructor

        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """
        self.__core_config = config
        self.__video_download_path = self.__core_config.video_download_path

        self.main_controller = main_controller
        self.restURLProvider = RestURLProvider(config)

    def getRequest(self, url):
        """
        This method is used to send a get request to the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :return: This method returns the original response including header as well as payload.
        """
        print("Send get request: " + str(url))
        try:
            response = requests.get(url)
        except Exception as e:
            print(f"GET threw an exception:\n{str(e)}\nExiting.")
            sys.exit()

        if response.status_code != 200:
            print(
                f"GET not successful:\n{response.status_code} {response.reason}\nExiting.")
            sys.exit()
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
        print("Send post request: " + str(url))
        try:
            response = requests.post(url=url, headers=headers, data=payload)
        except Exception as e:
            print(f"POST threw an exception:\n{str(e)}\nExiting.")
            sys.exit()

        print(f"Response: {response.status_code}")
        if response.status_code != 200:
            print(
                f"POST not successful:\n{response.status_code} {response.reason}\nExiting.")
            sys.exit()
        return response

    def getListofVideos(self):
        """
        This method is used to get a list of all available videos in the VHH-MMSI system.

        :return: This method returns a list of video objects (Class-type: Video) which holds all video specific meta-data.
        """
        url = self.restURLProvider.getUrlVideosList()
        res = requests.get(url, params={})
        res_json = res.json()

        video_instance_list = []
        for _, entry in enumerate(res_json['results']):
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
                                            processed_flag_shots=entry['tuwcvProcessedShots'],
                                            processed_flag_camera_movements=entry['tuwcvProcessedCameraMovements'],
                                            processed_flag_objects=entry['tuwcvProcessedObjects'],
                                            processed_flag_relations=entry['tuwcvProcessedRelations'],
                                            processed_flag_overscan=entry['tuwcvProcessedOverscan']
                                            )
                video_instance_list.append(video_instance)

        return video_instance_list

    def getRawAutomaticSTCResults(self, vid):
        """
        This method is used to get an automatic generated STC results from the VhhMMSI system.
        :param vid: This parameter must hold a valid video identifier.
        :return: This method returns the results (payload) as json format.
        """
        url = self.restURLProvider.getUrlShots(vid, auto = True)
        response = self.getRequest(url)
        return response.json()

    def getRawManualSTCResults(self, vid):
        """
        This method is used to get all manually generated STC results from the VhhMMSI system.
        :param vid: This parameter must hold a valid video identifier.
        :return: This method returns the results (payload) as json format.
        """
        url = self.restURLProvider.getUrlShots(vid, auto = False)
        response = self.getRequest(url)
        return response.json()

    def getRelations(self, vid):
        """
        Downloads manual public relations for a given VID.
        :return: This method returns the results (payload) as json format.
        """
        url = self.restURLProvider.getUrlRelations(vid)
        response = self.getRequest(url)
        return response.json()

    def downloadVideo(self, url, file_name, video_format):
        """
        This method is used to download a video from the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :param file_name: This parameter represents the filename on the local storage.
        :param video_format: This parameter must hold a valid video format extension (e.g. m4v)
        :return: This method returns a boolean flag which includes the state of the download process (true ... sucessfully finished OR false ... downlaod failed)
        """
        try:
            video_file = requests.get(url) 
            open(self.__video_download_path + "/" + file_name + "." +
                 str(video_format), 'wb').write(video_file.content)
            return True
        except:
            print("Download process failed!")
            return False

    def getAutoSTCResult(self, vid):
        """
        This method is used to download automatically generated shot results (STC) from the VhhMMSI system
        and transform them into a format that can be used by VHH packages.

        :return: A list of dictionaries that represent the STC file (in a format that can be directly stored as a csv)
        """
        res_json = self.getRawAutomaticSTCResults(vid)
        vid_name = f"{vid}.m4v"

        results = []
        shot_id_stc = 1
        for shot in res_json:
            if not 'cameraMovement' in shot.keys():
                results.append({'vid_name': vid_name, "shot_id": shot_id_stc,
                               "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "stc": shot["shotType"]})
                shot_id_stc += 1
        return results

    def downloadShotResults(self, vid):
        """
        This method is used to download shot results (SBD, STC) from the VhhMMSI system.

        :param vid: This parameter must hold a valid video identifier.
        """
        res_json = self.getRawAutomaticSTCResults(vid)

        file_name = str(vid) + ".csv"
        sbd_path = os.path.join(
            self.main_controller.get_result_directory("SBD"), file_name)
        stc_path = os.path.join(
            self.main_controller.get_result_directory("STC"), file_name)
        print("stc_path:", stc_path)

        with open(sbd_path, 'w') as sbd_file:
            with open(stc_path, 'w') as stc_file:
                # with open(cmc_path, 'w') as cmc_file:

                fieldnames_sbd = ["vid_name", "shot_id", "start", "end"]
                fieldnames_stc = ["vid_name", "shot_id", "start", "end", "stc"]

                writer_sbd = csv.DictWriter(
                    sbd_file, fieldnames=fieldnames_sbd, delimiter=";")
                writer_stc = csv.DictWriter(
                    stc_file, fieldnames=fieldnames_stc, delimiter=";")

                writer_sbd.writeheader()
                writer_stc.writeheader()

                vid_name = str(vid) + ".m4v"
                shot_id_stc = 1

                new_shots = []
                # The JSON does not contain information about shots with NA camera movement, need to add it by finding shots for which no camera movement is given
                for shot in filter(lambda x: 'shotType' in x.keys(), res_json):
                    if len(list(filter(lambda x: x["inPoint"] == shot["inPoint"] and x["outPoint"] == shot["outPoint"], res_json))) == 0:
                        new_shots.append(
                            {"inPoint": shot["inPoint"], "outPoint": shot["outPoint"]})

                res_json += new_shots
                # Sort numbers, so the shot ids are correct
                res_json.sort(key=lambda shot: shot["inPoint"])

                for shot in res_json:
                    writer_sbd.writerow({'vid_name': vid_name, "shot_id": shot_id_stc,
                                        "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1})
                    writer_stc.writerow({'vid_name': vid_name, "shot_id": shot_id_stc,
                                        "start": shot["inPoint"] - 1, "end": shot["outPoint"] - 1, "stc": shot["shotType"]})
                    shot_id_stc += 1

        return

    def postSBAResults(self, sba_paths):
        """
        Posts the automatically generated SBA results (SBD, STC) to the VhhMMSI system.

        :data: list of paths to json files that contain the shot information
        """
        for path in sba_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = self.restURLProvider.getUrlShots(vid, auto = True)
            with open(path) as file:
                data = json.load(file)
                print(path, "\n", data)
                self.postRequest(url, data)

    def postOBAResults(self, oba_paths):
        """
        Posts the automatically generated OBA results (ODT) to the VhhMMSI system.

        :data: list of paths to json files that contain the object information
        """
        for path in oba_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = self.restURLProvider.getUrlObjects(vid, auto = True) 
            with open(path) as file:
                data = json.load(file)
                self.postRequest(url, data)

    def postTBAResults(self, tba_paths):
        """
        Posts the automatically generated TBA results (CMC) to the VhhMMSI system.

        :data: list of paths to json files that contain the object information
        """
        for path in tba_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = self.restURLProvider.getUrlCameraMovements(vid, auto = True)
            with open(path) as file:
                data = json.load(file)
                self.postRequest(url, data)

    def postOSDresults(self, osd_list):
        """
        Posts overscan detections to VhhMMSI

        :osd_list: a list contatining a dictionary for each film
                    The dictionary contains the VID, and the overscan coordinates (left, right, top, bottom) normalized to to the intervall [0, 1]
        """
        for dict in osd_list:
            url = self.restURLProvider.getUrlOSD(dict["vid"], auto=True)
            self.postRequest(url, {
                "left": dict["left"],
                "right": dict["right"],
                "top": dict["top"],
                "bottom": dict["bottom"]
            })

    def postCMCResults(self, cmc_paths):
        """
        Posts the automatically generated CMC results (CMC) to the VhhMMSI system.

        :data: list of paths to json files that contain the shot information
        """
        for path in cmc_paths:
            vid = os.path.split(path)[-1].split('.')[0]
            url = self.restURLProvider.getUrlCameraMovements(vid, auto = True)

            with open(path) as file:
                data = json.load(file)

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

                self.postRequest(url, results)
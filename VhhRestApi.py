import json
import requests
from Video import Video


class VhhRestApi(object):
    """
    This class includes the interfaces and methods to use the vhh restAPI interfaces provided by MaxRecall.
    """

    def __init__(self, config=None):
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
        self.API_VIDEO_SEARCH_ENDPOINT = self.__root_url + "/videos/search"
        self.API_VIDEO_SHOTS_AUTO_ENDPOINT = self.__root_url + "/videos/"  # 8/shots/auto

    def getRequest(self, url):
        """
        This method is used to send a get request to the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :return: This method returns the original response including header as well as payload.
        """
        print("send request: " + str(url))
        response = requests.get(url, verify=self.__pem_path)  # params=params,
        print("receive response")
        # print(res)
        return response

    def postRequest(self, url, data_dict):
        """
        This method is used to send a post request to the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :param data_dict: this parameter must hold a valid list of dictionaries with the specified fields (see RestApi documentation).
        :return: This method returns the original response including header as well as payload
        """
        headers = {"Content-Type ": "application/json"}
        payload = json.dumps(data_dict)

        print("send request: " + str(url))
        response = requests.post(url=url, headers=headers, data=payload, verify=self.__pem_path)  # , header=headers
        print("receive response")
        # print(res)
        return response

    def getListofVideos(self):
        """
        This method is used to get a list of all available videos in the VHH-MMSI system.

        :return: This method returns a list of video objects (Class-type: Video) which holds all video specific meta-data.
        """
        print("load list of videos ... ")

        print("send request: " + str(self.API_VIDEO_SEARCH_ENDPOINT))
        res = requests.get(self.API_VIDEO_SEARCH_ENDPOINT ) #, verify=self.__pem_path)  # params=params,
        print("receive response")

        res_json = res.json()

        video_instance_list = []
        for i in range(0, len(res_json)):
            entry = res_json[i]
            vid = int(entry['id'])
            originalFileName = entry['originalFileName']
            url = entry['url']

            # filter frame_counter videos and amX videos
            if not "video-framecounter" in originalFileName and not "eyeland" in originalFileName and not "am-" in originalFileName:
                video_instance = Video(self.__core_config)
                video_instance.create_video(vid=vid,
                                            originalFileName=originalFileName,
                                            url=url,
                                            download_path=self.__video_download_path)
                video_instance_list.append(video_instance)

        return video_instance_list

    def downloadVideo(self, url, file_name, video_format):
        """
        This method is used to download a video from the Vhh-MMSI system.

        :param url: this parameter must hold a valid restApi endpoint.
        :param file_name: This parameter represents the filename on the local storage.
        :param video_format: This parameter must hold a valid video format extension (e.g. m4v)
        :return: This method returns a boolean flag which includes the state of the download process (true ... sucessfully finished OR false ... downlaod failed)
        """
        print("start download process ... ")
        ret = False

        try:
            video_file = requests.get(url, verify=self.__pem_path)
            open(self.__video_download_path + "/" + file_name + "." + str(video_format), 'wb').write(video_file.content)
            print("successfully downloaded ... ")
            ret = True
        except():
            print("Download process failed!")
            ret = False

        return ret

    def getAutomaticResults(self, vid):
        """
        This method is used to get all automatic generated results from the VhhMMSI system.

        :param vid: This parameter must hold a valid video identifier.
        :return: THis method returns the results (payload) as json format.
        """

        print("get sbd results from maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        response = self.getRequest(url)
        res_json = response.json()
        print(res_json)
        return res_json

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
        #print(json.dumps(data_dict_l))

        #payload = json.dumps(data_dict_l)
        #print(payload)

        response = self.postRequest(url, data_dict_l)
        #print(response.content)


        print("sbd results successfully sent to maxrecall ... ")

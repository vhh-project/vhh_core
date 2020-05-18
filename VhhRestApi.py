import numpy as np
import json
import requests
from Video import Video


class VhhRestApi(object):
    def __init__(self, config=None):
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
        print("send request: " + str(url))
        response = requests.get(url, verify=self.__pem_path)  # params=params,
        print("receive response")
        # print(res)
        return response

    def postRequest(self, url, data_dict):
        headers = {"Content-Type ": "application/json"}
        payload = json.dumps(data_dict)

        print("send request: " + str(url))
        response = requests.post(url=url, headers=headers, data=payload, verify=self.__pem_path)  # , header=headers
        print("receive response")
        # print(res)
        return response

    def getListofVideos(self):
        print("load list of videos ... ")

        print("send request: " + str(self.API_VIDEO_SEARCH_ENDPOINT))
        res = requests.get(self.API_VIDEO_SEARCH_ENDPOINT, verify=self.__pem_path)  # params=params,
        print("receive response")
        print(res)

        res_json = res.json()
        print(type(res_json))
        print(len(res_json))

        print(res_json[0])
        print(res_json[0].keys())

        video_instance_list = []
        for i in range(0, len(res_json)):
            entry = res_json[i]
            vid = int(entry['id'])
            originalFileName = entry['originalFileName']
            url = entry['url']

            video_instance = Video(self.__core_config)
            video_instance.create_video(vid=vid,
                                        originalFileName=originalFileName,
                                        url=url,
                                        download_path=self.__video_download_path)
            video_instance_list.append(video_instance)

        return video_instance_list

    def downloadVideo(self, url, file_name, video_format):
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
        print("get sbd results from maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        response = self.getRequest(url)
        res_json = response.json()
        print(res_json)
        return res_json

    def postAutomaticResults(self, vid, results_np):
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
        print(response.content)


        print("sbd results successfully sent to maxrecall ... ")

import numpy as np
import json
import requests
from Video import Video


class VhhRestApi():
    def __init__(self,
                 root_url="https://api.vhh-stg.max-recall.com/api/shotservice/",
                 pem_path="/home/dhelm/VHH_Develop/certificates/cacert.pem",
                 video_download_path="/data/share/maxrecall_vhh_mmsi/videos/downloaded/"):

        print("create instance of VhhRestApi ...")
        self.root_url = root_url
        self.pem_path = pem_path

        # download path
        self.video_download_path = video_download_path

        # create urls
        self.API_VIDEO_SEARCH_ENDPOINT = root_url + "/videos/search"
        self.API_VIDEO_SHOTS_AUTO_ENDPOINT = self.root_url + "/videos/"  # 8/shots/auto

    def getRequest(self, url):
        print("send request: " + str(url))
        response = requests.get(url, verify=self.pem_path)  # params=params,
        print("receive response")
        # print(res)
        return response

    def postRequest(self, url, data_dict):
        headers = {"Content-Type ": "application/json"}
        payload = json.dumps(data_dict)

        print("send request: " + str(url))
        response = requests.post(url=url, headers=headers, data=payload, verify=self.pem_path)  # , header=headers
        print("receive response")
        # print(res)
        return response

    def getListofVideosFromMaxRecall(self):
        print("load list of videos ... ")

        print("send request: " + str(self.API_VIDEO_SEARCH_ENDPOINT))
        res = requests.get(self.API_VIDEO_SEARCH_ENDPOINT, verify=self.pem_path)  # params=params,
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

            video_instance = Video(vid=vid,
                                   originalFileName=originalFileName,
                                   url=url)
            video_instance_list.append(video_instance)

        return video_instance_list

    def downloadVideo(self, url, file_name, video_format):
        print("start download process ... ")
        video_file = requests.get(url, verify=self.pem_path)
        open(self.video_download_path + "/" + file_name + "." + str(video_format), 'wb').write(video_file.content)
        print("successfully downloaded ... ")

    def getAutomaticSbdResults(self, vid):
        print("get sbd results from maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + str(vid) + "/shots/auto"
        response = self.getRequest(url)
        res_json = response.json()
        print(res_json)

    def postAutomaticSbdResults(self, vid, results_np):
        print("save sbd results to maxrecall ... ")
        url = self.API_VIDEO_SHOTS_AUTO_ENDPOINT + "/" + str(vid) + "/shots/auto"

        data_block = results_np[1:, :]

        data_dict_l = []
        for i in range(0, len(data_block)):
            inpoint = int(data_block[i][2]) + 1
            outpoint = int(data_block[i][3]) + 1

            data_dict = {
                "inPoint": inpoint,
                "outPoint": outpoint,
                "shotType": "MS",
                "cameraMovement": "PAN"
            }

            data_dict_l.append(data_dict)
        #print(json.dumps(data_dict_l))

        payload = json.dumps(data_dict_l)
        response = self.postRequest(url, payload)
        print(response.content)

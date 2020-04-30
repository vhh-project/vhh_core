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
        self.url_video_list = "https://api.vhh-stg.max-recall.com/api/shotservice/videos/search"


    def getListofVideosFromMaxRecall(self):
        print("load list of videos ... ")

        print("send request: " + str(self.url_video_list))
        res = requests.get(self.url_video_list, verify=self.pem_path)  # params=params,
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
'''
# curl -X GET "https://api.vhh-stg.max-recall.com/api/shotservice/" --cacert /home/dhelm/VHH_Develop/certificates/cacert.pem
# https://imediacities.hpc.cineca.it/api/videos/a4cb3b82-8771-495f-b2ad-11d479258216/shots
'''
from typing import List
from urllib.parse import urljoin
from functools import reduce

class RestURLProvider(object):
    """
    This class provides all URLs to access VhhMMSI. 
    """

    def __init__(self, config):
        """
        :param config: parameter must hold the core configuration object (Class-type Configuration)
        """
        self.__root_url = config.root_url
        self.ENDPT_VIDEOS = urljoin(self.__root_url, "videos/")

    def join_video_endpt(self, url_list: List[str]):
        """
        Concatenates the list of parameters to the video enpoint url.
            E.g. for [1234, "shots/auto"] this will return 
            "https://api.vhh-mmsi.eu/api/tbaservice/videos/1234/shots/auto"
        """
        entire_url_list = [self.ENDPT_VIDEOS] + url_list
        return reduce(urljoin, entire_url_list)

    def join_video_endpt_with_vid(self, vid: int, auto: bool, url_list: List[str]):
        entire_url_list = [f"{vid}/"] + url_list + ["auto/" if auto else "manual/"]
        return self.join_video_endpt(entire_url_list)

    def getUrlVideosList(self):
        return self.join_video_endpt(["search/"])

    def getUrlShots(self, vid: int, auto: bool = True):
        if auto:
            return self.join_video_endpt_with_vid(vid, auto, ["shots/"])
        else:
            return self.join_video_endpt([f"{vid}/tbas/public/shots/manual"])

    def getUrlObjects(self, vid: int, auto: bool = True):
        return self.join_video_endpt_with_vid(vid, auto, ["objects/"])
    
    def getUrlTba(self, vid: int, ):
        return self.join_video_endpt([f"{vid}/tbas/public/"])

    def getUrlCameraMovements(self, vid: int, auto: bool = True):
        return self.join_video_endpt_with_vid(vid, auto, ["camera-movements/"])

    def getUrlOSD(self, vid: int, auto: bool = True):
        if auto:
            return self.join_video_endpt_with_vid(vid, auto, ["overscan/"])
        else:
            return self.join_video_endpt([f"{vid}/overscan"])


    def getUrlRelations(self, vid: int):
        return self.join_video_endpt([f"{vid}/", "relations/public"])

    def addListOfParametersToUrl(self, url, parameter_dict={}):
        entire_parameter_l = [f'{parameter}={value}' for parameter, value in zip(parameter_dict.keys(), parameter_dict.values())]
        seperator = "&"
        entire_parameter_url = seperator.join(entire_parameter_l)
        entire_url_list = f"{url}?" + entire_parameter_url
        return entire_url_list


    def getUrlPublicTbaShots(self, vid: int, annotation_mode="auto", isPublished=False, isConfirmed=False):
        # annotation_mode: auto | manual | all
        if annotation_mode == "all":
            entire_url = self.join_video_endpt([f"{vid}/tbas/public/shots"])
        else:
            entire_url = self.join_video_endpt([f"{vid}/tbas/public/shots/{annotation_mode}"])
            parameter_dict = {
                "isPublished": isPublished,
                "isConfirmed": isConfirmed
            }
            entire_url = self.addListOfParametersToUrl(entire_url, parameter_dict)

        return entire_url



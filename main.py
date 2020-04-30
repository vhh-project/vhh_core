from sbd.SBD import SBD
from sbd.utils import *
from VhhRestApi import VhhRestApi

import os
'''
printCustom("Welcome to the sbd framework!", STDOUT_TYPE.INFO);
printCustom("Setup environment variables ... ", STDOUT_TYPE.INFO)
print("------------------------------------------")
print("LD_LIBRARY_PATH: ", str(os.environ['LD_LIBRARY_PATH']))
print("CUDA_HOME: ", str(os.environ['CUDA_HOME']))
print("PATH: ", str(os.environ['PATH']))
print("CUDA_VISIBLE_DEVICES: ", str(os.environ['CUDA_VISIBLE_DEVICES']))
print("PYTHONPATH: ", str(os.environ['PYTHONPATH']))
print("------------------------------------------")
'''

def run_sbd_process(video_path, file_name, config_file):
    printCustom("start sbd process ... ", STDOUT_TYPE.INFO)

    # read commandline arguments
    #params = getCommandLineParams();

    # run shot boundary detection process
    video_filename = os.path.join(video_path + file_name)

    # initialize and run sbd process
    sbd_instance = SBD(config_file);
    sbd_instance.runOnSingleVideo(video_filename);
    printCustom("sbd process finished!", STDOUT_TYPE.INFO)


def main():

    root_url = "https://api.vhh-stg.max-recall.com/api/shotservice/",
    pem_path = "/home/dhelm/VHH_Develop/certificates/cacert.pem"
    video_download_path = "/data/share/maxrecall_vhh_mmsi/videos/downloaded/"
    '''
    rest_api_instance = VhhRestApi(root_url=root_url, pem_path=pem_path, video_download_path=video_download_path)

    video_list = rest_api_instance.getListofVideosFromMaxRecall()

    print("start download process ... ")
    for video in video_list:
        video.printInfo()

        rest_api_instance.downloadVideo(video.url, video.originalFileName, video.video_format)
    print("download process finished ... ")
    '''

    video_list = os.listdir(video_download_path)
    print(video_list)
    config_file = "/home/dhelm/VHH_Develop/pycharm_vhh_core/config/config_single_video.yaml"

    video_path = video_download_path
    file_name = video_list[0]
    run_sbd_process(video_path=video_path, file_name=file_name, config_file=config_file)



if __name__ == '__main__':
    main()
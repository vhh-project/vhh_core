from sbd.SBD import SBD
from sbd.utils import *
from VhhRestApi import VhhRestApi
import numpy as np
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

    root_url = "https://api.vhh-stg.max-recall.com/api/shotservice/"
    pem_path = "/home/dhelm/VHH_Develop/certificates/cacert.pem"
    video_download_path = "/data/share/maxrecall_vhh_mmsi/videos/downloaded/"

    rest_api_instance = VhhRestApi(root_url=root_url, pem_path=pem_path, video_download_path=video_download_path)


    # get film list with urls
    '''
    video_list = rest_api_instance.getListofVideosFromMaxRecall()
    
    print("start download process ... ")
    for video in video_list:
        video.printInfo()
        rest_api_instance.downloadVideo(video.url, video.originalFileName, video.video_format)
    print("download process finished ... ")
    '''

    # run sbd

    video_list = os.listdir(video_download_path)
    video_list = [video_list[3]]
    print(video_list)
    #exit()
    config_file = "/home/dhelm/VHH_Develop/pycharm_vhh_core/config/SBD/config_single_video.yaml"

    video_path = video_download_path
    for video in video_list:
        file_name = video
        run_sbd_process(video_path=video_path, file_name=file_name, config_file=config_file)
    ''''''


    # prepare results and send it to maxrecall
    '''
    results_path = "/data/share/maxrecall_vhh_mmsi/videos/results/sbd/final_results/"
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
        entries.append([line_split[0], line_split[1], line_split[2], line_split[3]])
    entries_np = np.array(entries)
    print(entries_np)

    rest_api_instance.postAutomaticSbdResults(vid=10,
                                              results_np=entries_np)
    '''

    rest_api_instance.getAutomaticSbdResults(vid=10)

if __name__ == '__main__':
    main()
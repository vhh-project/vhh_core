"""
Pushes the result of relation detection module to VhhMMSI
Run with
    python Develop/post_rd_results.py $PATH
    where $path is a path to a folder containing RD results (features as numpy files)
"""

import os
import json
import argparse
import glob
import pickle
import numpy as np
from tqdm import tqdm

from MainController import MainController


def do_pickle(data, filepath):
    outfile = open(filepath,'wb')
    pickle.dump(data,outfile)
    outfile.close()

def do_unpickle(filepath):
    with open(filepath, 'rb') as pickleFile:
        return pickle.load(pickleFile)

def load_features(img_name, rd):
    """
    Given an img name, loads the corresponding feature
    """
    features_path = rd.get_feature_path(img_name)
    return do_unpickle(features_path) 


def main():
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-p', '--path', dest='path', help="The download directory for the results,  for example: '-p /data/ext/VHH/datasets/vhh_mmsi_v1_5_0_relation_db/vhh_rd_data/'. Must be a valid directory.", required=True)
    required_args.add_argument('-b', '--backbone', dest='backbone', help="The name of the feature extractor model,  for example: '-b resnet18'. Must be a valid directory/model included in the path (--path).", required=True)
    args  = parser.parse_args()

    if not os.path.isdir(args.path):
        raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

    if args.backbone is None:
        raise ValueError("You have to specify a valid backbone model. Call this script with the '-h' parameter to get information on how to run it")

    features_path = os.path.join(args.path, "FinalResults")
    features_path = os.path.join(features_path, args.backbone)
    final_features_path = glob.glob(os.path.join(features_path, "*.pickle"))
    print(f"Found {len(final_features_path)} feature-files")
       
    main_instance = MainController()
    api = main_instance.get_rest_api()
        
    # debug filter
    white_list = ["8317", "8293", "8289", "8286", "8287", "8288", "8455", "8292", "8396", "8291", "8295", "8359", "8366", "8358", "8369", "8370", "8386", "8398", "8456", "8294", "8347", "8443", "8400", "8408", "8385", "8368", "8399", "8397", "8525", "8395", "8367", "8442", "8417", "8522", "8335", "8389", "8388", "8406", "8520", "8345", "8448", "9302", "8450", "8451", "8519", "8342", "8387", "9248", "8523", "8357", "8521", "8447", "8391", "8524", "8394", "9242", "8355", "8316", "8374", "8410", "9230", "8321", "8402", "9245", "8379", "8414", "8421", "8322", "8349", "8319", "8344", "9234", "9233", "8383", "9249", "9284", "8280", "8364", "9238", "9247", "8373", "8392", "9232", "8332", "9226", "8415", "8444", "8518", "8328", "8276", "9235", "9237", "8337", "8284", "8330", "8390", "9243", "8412", "9240", "9299", "8371", "8384", "8411", "9288", "8381", "8325", "8327", "8354", "9301", "8353", "8360", "9229", "9231", "9251", "8363", "8418", "8320", "8331", "9236", "8326", "9241", "8382", "9286", "9244", "9239", "8324", "8343", "8346", "8428", "8334", "8336", "8340", "8329", "8407", "8419", "9228", "8425", "9285", "8318", "8413", "8437", "9227", "8393", "8380", "9300", "8323", "8424", "8339", "8416", "8469", "8361", "9295", "8426", "8341", "9287", "8439", "8338", "9296", "9294", "9293", "8315", "9290", "9298", "9297", "8401", "9292", "8216", "8365", "9291", "9289"]   
    # NOT WORKING: "8348", "8351", "8352" "8356" "8362" "8405" "8409" "8422" "8423"  "8427" "8440" "8441" "8445" "8446" "8449"
    
    
    
    entries_l = []
    rd_dict_l = []
    cnt = 0
    print("Loading features ... ")
    for feature_path in tqdm(final_features_path):
        filename = feature_path.split("/")[-1]
        filename_without_extension = filename.split(".")[0]
        filename_without_extension_split = filename_without_extension.split("_")
        
        start_idx = filename_without_extension.find("tbaid") + 6
        end_idx = filename_without_extension.find("model") - 1
        tba_id = filename_without_extension[start_idx:end_idx]

        fids_l = []
        idx = filename_without_extension_split.index("frame")
        fid = filename_without_extension_split[idx + 1]
        fids_l.append(int(fid))

        idx = filename_without_extension_split.index("id")
        vid = filename_without_extension_split[idx + 1]

        idx = filename_without_extension_split.index("model")
        model_name = filename_without_extension_split[idx + 1]

        idx = filename_without_extension_split.index("sid")
        sid = filename_without_extension_split[idx + 1]

        entries_l.append([vid, fid, sid, tba_id, model_name, feature_path])

    entries_np = np.array(entries_l)
    vids_np = entries_np[:, :1]
    unique_vids = np.unique(vids_np).astype('int').tolist()

    for vid in unique_vids:
        if str(vid) not in white_list: 
            continue

        # filter all files of same vid
        idx = np.where(vid == vids_np.astype('int'))[0]
        entries_of_vid_np = entries_np[idx, :]

        print(f'process vid: {vid}')

        # iterate over all entries of individual vid
        rd_dict_l = []
        for i in range(0, len(entries_of_vid_np)):
            vid = entries_of_vid_np[i][0]
            fid = entries_of_vid_np[i][1]
            sid = entries_of_vid_np[i][2]
            tba_id = entries_of_vid_np[i][3]
            model_name = entries_of_vid_np[i][4]
            feature_path = entries_of_vid_np[i][5]

            feature_vector = do_unpickle(feature_path)
            value_source = "TUW CV relation detection v1" + " (" + model_name + ")" 

            rd_dict = {
                "tbaId": tba_id,
                "featureVector": feature_vector.tolist(), 
                "featureVectorFrameIds": fids_l,
                "featureVectorValueSource": value_source
            }
            rd_dict_l.append(rd_dict)
        
        print(len(rd_dict_l))
        cnt = cnt + 1

        # Post data per vid to VhhMMSI
        api.postRdResults(vid, rd_dict_l)

        

    print(f'number of processed videos: {cnt}')

if __name__ == "__main__":
    main()

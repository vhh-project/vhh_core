"""
Given a directory of relations (can be generated via download_relations.py)
this script will generate the video sequences for each relation of selected VIDs

Example use:

"""

import argparse
import glob
import json
import os
import shutil

import cv2

from VhhRestApi import VhhRestApi
from Configuration import Configuration
from compare_videos import main as compare_videos

config_file = "../config/CORE/config.yaml"

def join_path_mkdir_if_not_exists(path, dir_name):
    """
    Combines path + dir_name and creates this directory if it does not yet exists
    Returns the combined path
    """
    new_path = os.path.join(path, dir_name)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    return new_path

def get_relations_path(data_path, id):
    """
    Returns a path to the relation for a given id
    """
    return os.path.join(data_path, f"relations_{id}.json")

def download_video(RestAPI, tmp_path, video_list, id):
    """
    For a given ID, downloads the video unless it is already stored
    Returns path to video
    """

    video_path = os.path.join(tmp_path, f"{id}.m4v")
    # Check if video already exists
    if os.path.exists(video_path):
        return video_path

    # Get video instance
    relevant_videos = list(filter(lambda v: v.id == int(id), video_list))
    assert len(relevant_videos) == 1
    video = relevant_videos[0]

    video.download(RestAPI)
    return video_path

def generate_snippet(RestAPI, path_snippet, tmp_path, video_list, id, inPoint, outPoint):
    """
    Stores a snippet at the given path
    1 must be subtracted from inPoint and outPoint BEFORE this function if the data comes from VhhMMSI
    """
    # Check if snippet exists
    if os.path.exists(path_snippet):
        return


    video_path = download_video(RestAPI, tmp_path, video_list, id)
    
    # Collect images
    images = []
    print(inPoint, outPoint)

    cap = cv2.VideoCapture(video_path)

    # So we at least get something
    if inPoint == outPoint:
        outPoint += 1

    for frame in range(inPoint, outPoint):
        cap.set(1, frame)
        ret, img = cap.read()

        if not ret:
            print("Failed")
            continue
        images.append(img)

    # Store snippet
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path_snippet, fourcc, 24, (images[0].shape[1], images[0].shape[0]))
    for img in images:
        out.write(img)
    out.release()

# Parse arguments
parser = argparse.ArgumentParser(description="Generate sequences from relations")

parser.add_argument('-i', '--id', nargs='+', dest = "ids", type=int, help = 
    "Specify ids of videos that whose sequences you want to generate, for example: '-i 8213 8214'. Cannot be used together with '-a'.")
parser.add_argument('-a', '--all', dest='generate_all', action='store_true', help = "If this parameter is used then all sequences who are stored in the given path will be generated.")

required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='output_path', help =
    "The download directory for the results,  for example: '-p /data/share/fjogl/sequences/'. Must be a valid directory.", required=True)

required_args.add_argument('-d', '--data', dest='data_path', help =
    "The path containing the relation json files,  for example: '-p /data/share/fjogl/relations_test/'. Must be a valid directory.", required=True)

args = parser.parse_args()

# Check arguments
if not os.path.isdir(args.output_path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

if not os.path.isdir(args.data_path):
    print(args.data_path)
    raise ValueError("data must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

if args.generate_all and args.ids is not None:
    raise ValueError("'-a' cannot be used together with '-i'")
    
if not args.generate_all and args.ids is None:
    raise ValueError("Either '-a' or '-i' must be used")

if args.ids is not None:
    for id in args.ids:
        if not os.path.exists(get_relations_path(args.data_path, id)):
            raise ValueError(f"There exists no relation json for film with VID {id}")

tmp_path = join_path_mkdir_if_not_exists(args.output_path, "tmp")


# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()
configuration_instance.video_download_path = tmp_path
RestAPI = VhhRestApi(config=configuration_instance)

# Collect ids
if args.generate_all:
    relations = glob.glob(os.path.join(args.data_path, "*.json"))
    file_names = map(lambda path: os.path.split(path)[-1], relations)
    ids = list(map(lambda filename: filename[10:14], file_names))
else:
    ids = args.ids

video_list = RestAPI.getListofVideos()

# MAIN PART
for id in ids:
    # Create directories
    film_dir_path = join_path_mkdir_if_not_exists(args.output_path, str(id))

    # Load relation
    with open(os.path.join(get_relations_path(args.data_path, id))) as file:
        relations = json.load(file)

    for count, relation in enumerate(relations):
        # Only support frame range for now
        if relation["leftType"] != "frame_range" or relation["rightType"] != "frame_range":
            continue

        output_path = join_path_mkdir_if_not_exists(film_dir_path, f"Relation_{count}")

        left_snippet_path = os.path.join(output_path, "left.m4v")
        right_snippet_path = os.path.join(output_path, "right.m4v")

        generate_snippet(RestAPI,  left_snippet_path, tmp_path, video_list, relation["leftValue"], relation["leftStart"], relation["leftEnd"])
        generate_snippet(RestAPI,  right_snippet_path, tmp_path, video_list, relation["rightValue"], relation["rightStart"], relation["rightEnd"])

        with open(os.path.join(output_path, "relation.json"), 'w') as file:
            json.dump(relation, file)

        compare_videos(left_snippet_path, right_snippet_path, f"Left {relation['leftValue']}", f"Right {relation['rightValue']}", os.path.join(output_path, "comparison.m4v"))

    # Store relations json
    with open(os.path.join(film_dir_path, "relation.json"), 'w') as file:
        json.dump(relations, file)


# Delete temporary directory
shutil.rmtree(tmp_path)

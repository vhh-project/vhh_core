from VhhRestApi import VhhRestApi
from Configuration import Configuration
import argparse, os
import Utils

"""
Download the metadata for all videos and stores it as CSV and JSON.
For more details on the parameters please call this script with the parameter '-h'
Needs to be run from INSIDE the Develop directory
"""

config_file = "../config/CORE/config.yaml"
output_filename = "metadata"

#
# ARGUMENT PARSING
#

parser = argparse.ArgumentParser(description="Download video metadata")

# This is a required parameter
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
"The download directory for the results,  for example: '-p /data/share/USERNAME/metadata/'. Must be a valid directory.", required=True)

args = parser.parse_args()


if not os.path.isdir(args.path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()

# Set download path to specified path
configuration_instance.video_download_path = args.path
RestAPI = VhhRestApi(config=configuration_instance)

video_list = RestAPI.getListofVideos()
print("There exist {0} video in total".format(len(video_list)))

# Store metadata in resuls list
metadata = []
for video in video_list:
    metadata.append({"id": video.id, "originalFileName": video.originalFileName, "url": video.url, 
    "video_format": video.video_format, "file_name": video.file_name, "processed_flag": video.processed_flag})

file_name_without_extension = os.path.join(args.path, output_filename)

file_path_csv = Utils.make_filepath_unique(file_name_without_extension, '.csv')
file_path_json = Utils.make_filepath_unique(file_name_without_extension, '.json')

Utils.store_csv(file_path_csv, metadata)
Utils.store_json(file_path_json, metadata)

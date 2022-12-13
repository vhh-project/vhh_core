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

parser.add_argument('-s', '--starting_with', dest='starting_with', nargs='+', type=str, help = """Download all videos starting with this i.e. "-s NARA EFA LOC" will only download videos who's name starts with NARA, EFA or LOC""")
parser.add_argument('-r', '--remove_fields', dest='remove_fields', nargs='+', type=str, help = 
    """Does not store these fields from the metadata i.e. "-r processed_shots processed_objects processed_relations processed_overscan" will get rid of all the processing information.""")

# This is a required parameter
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
"The download directory for the results,  for example: '-p /data/share/USERNAME/metadata/'. Must be a valid directory.", required=True)

args = parser.parse_args()

# List of strings that a videoname must start with
prefixes = args.starting_with

# If no prefixes are given then accept every video
if prefixes is None:
    prefixes = [""]

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
    if any([video.originalFileName.startswith(prefix) for prefix in prefixes]):
        metadata.append({"id": video.id, "originalFileName": video.originalFileName, "url": video.url, 
        "video_format": video.video_format, "file_name": video.file_name, "processed_shots": video.processed_flags["shots"],
        "processed_objects": video.processed_flags["objects"], "processed_relations": video.processed_flags["relations"],
        "processed_overscan" : video.processed_flags["overscan"]})

file_name_without_extension = os.path.join(args.path, output_filename)

file_path_csv = Utils.make_filepath_unique(file_name_without_extension, '.csv')
file_path_json = Utils.make_filepath_unique(file_name_without_extension, '.json')

# Remove the specified fields:
if not args.remove_fields is None:
    for metadata_dict in metadata:
        for field in args.remove_fields:
            del metadata_dict[field]

Utils.store_csv(file_path_csv, metadata)
Utils.store_json(file_path_json, metadata)

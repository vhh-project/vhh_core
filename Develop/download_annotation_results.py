from VhhRestApi import VhhRestApi
from Configuration import Configuration
import argparse, os
import Utils

"""
Download all annotation results.
For more details on the parameters please call this script with the parameter '-h'
Needs to be run from INSIDE the Develop directory
"""

config_file = "../config/CORE/config.yaml"
output_filename = "annotation_results"

#
# ARGUMENT PARSING
#

parser = argparse.ArgumentParser(description="Download annotation results")

parser.add_argument('-i', '--id', nargs='+', dest = "ids", type=int, help = 
"Specify ids of videos that whose annotation result you want to download, for example: '-i 8213 8214'. Cannot be used together with -a")
parser.add_argument('-a', '--all', dest='download_all', action='store_true', help = "If this parameter is used then download all annotated videos.")
parser.add_argument('-c', '--csv', dest='store_as_csv', action='store_true', help = "If this parameter is used then the results will be stores as CSV.")
parser.add_argument('-j', '--json', dest='store_as_json', action='store_true', help = "If this parameter is used then the results will be stores as JSON.")
parser.add_argument('-s', '--separate-files', dest='store_separate_files', action='store_true', help = "If this parameter is used then the results will in separate files, one for each id.")
parser.add_argument('-o', '--one-file', dest='store_one_file', action='store_true', help = "If this parameter is used then the results will be stored in one big file.")

# This is a required parameter
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
"The download directory for the results,  for example: '-p /data/share/USERNAME/results/'. Must be a valid directory.", required=True)

parser.set_defaults(download_all=False)
parser.set_defaults(store_as_csv=False)
parser.set_defaults(store_as_json=False)
parser.set_defaults(store_separate_files=False)
parser.set_defaults(store_one_file=False)
args = parser.parse_args()

if not args.store_one_file and not args.store_separate_files:
    raise ValueError(
        "Neither -s nor -o parameter used. This would mean the result will neither be stored in one single file (-o) or in separate files for each id (-s). Please use at least one of -s or -o.  Call this script with the '-h' parameter to get information on how to run it")

if not os.path.isdir(args.path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

if args.ids is not None and args.download_all:
    raise ValueError("Cannot specify ids and download all annotation results. Call this script with the '-h' parameter to get information on how to run it")


#
# MAIN PART OF SCRIPT
#

# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()

# Set download path to specified path
configuration_instance.video_download_path = args.path
RestAPI = VhhRestApi(config=configuration_instance)

# Create a list of ids for which we want to download the annotation results
if args.download_all:
    # Create a list that has the id of every video that is annotated
    videos_id_list = []
    videos_list = RestAPI.getListofVideos()
    for video in videos_list:
        if video.processed_flag:
            videos_id_list.append(video.id)
else:
    videos_id_list = args.ids

print("Found {0} videos that fulfill the requirements".format(len(videos_id_list)))

annotation_results = []

# Get annotation results
for vid in videos_id_list:
    RestAPI.downloadSTCData(vid, args.path)
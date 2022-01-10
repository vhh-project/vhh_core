from VhhRestApi import VhhRestApi
from Configuration import Configuration
import argparse, os, sys

"""
Download all videos that fulfill certain criterias.
For more details on the parameters please call this script with the parameter '-h'
Needs to be run from INSIDE the Develop directory
"""

config_file = "../config/CORE/config.yaml"

#
# ARGUMENT PARSING
#

parser = argparse.ArgumentParser(description="Download all videos that fulfill certain criterias.")

parser.add_argument('-i', '--id', nargs='+', dest = "ids", type=int, help = 
"Specify ids of videos that you want to download, for example: '-i 8213 8214'. Cannot be used together with -a or -n")
parser.add_argument('-a', '--annotated', dest='use_annotated', action='store_true', help = "If this parameter is used then download all annotated videos.")
parser.add_argument('-n', '--not-annotated', dest='use_not_annotated', action='store_true', help = "If this is parameter is used then download all not annotated videos.")
parser.add_argument('-m', "-max_number", dest="max_number_of_downloads", nargs = '?', type=int, const=5, help =
"The maximum number of videos to download, for example '-m 2'. Default value is 5. To download without a maximum number set this to -1. ")

parser.add_argument('-s', '--starting_with', dest='starting_with', nargs='?', type=str, const = "", help = "Download all videos starting with this i.e. -s NARA will only download videos who's name starts with NARA")
parser.add_argument('--full_name', dest='use_full_name', action='store_true', help = "If this parameter is used then videos will be stored as ID_(full_name).FILEENDING")


# This is a required parameter
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
"The download directory for the videos,  for example: '-p /data/share/USERNAME/videos'. Must be a valid directory.", required=True)

parser.set_defaults(use_annotated=False)
parser.set_defaults(use_not_annotated=False)
args = parser.parse_args()

if not os.path.isdir(args.path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

if args.ids is not None and (args.use_annotated or args.use_not_annotated):
    raise ValueError("Cannot specify ids and download all annotated / not annotated video. Call this script with the '-h' parameter to get information on how to run it")

#
# MAIN PART OF SCRIPT
#

# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()

# Set download path to specified path
configuration_instance.video_download_path = args.path
RestAPI = VhhRestApi(config=configuration_instance)

video_list = RestAPI.getListofVideos()
print("There exist {0} video in total".format(len(video_list)))

# Collect the videos that fulfill the criteria (processed / non processed / ID)
videos_selected = []
for video in video_list:

    # Only use videos that start with the required string
    if not video.originalFileName.startswith(args.starting_with):
        continue

    if args.use_annotated and video.processed_flag:
        videos_selected.append(video)
    elif args.use_not_annotated and not video.processed_flag:
        videos_selected.append(video)
    elif args.ids is not None and video.id in args.ids:
        videos_selected.append(video)
     

print("Found {0} videos that fit the criteria".format(len(videos_selected)))
if len(video_list) == 0:
    sys.exit()

print("Storing videos into path: {0}".format(args.path))

# Download videos, do not download more videos than the maximum allowed amount
number_downloads = 0
for video in videos_selected:
    if number_downloads == args.max_number_of_downloads:
        break
    print("Video {0} ({1})".format(video.id, video.originalFileName))
    if not video.is_downloaded():
        number_downloads += 1

        if args.use_full_name:
            video.download(RestAPI, "{0}_({1})".format(video.id, video.originalFileName))
        else:
            video.download(RestAPI)

    
print("Downloaded {0} videos".format(number_downloads))

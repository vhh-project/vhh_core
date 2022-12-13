import argparse
import json
import os

from VhhRestApi import VhhRestApi
from Configuration import Configuration

config_file = "../config/CORE/config.yaml"

# Parse arguments
parser = argparse.ArgumentParser(description="Download overscan annotations")

parser.add_argument('-i', '--id', nargs='+', dest = "ids", type=int, help = 
    "Specify ids of videos that whose relations you want to download, for example: '-i 8213 8214'. Cannot be used together with '-a'.")
parser.add_argument('-a', '--all', dest='download_all', action='store_true', help = "If this parameter is used then download all public relations.")

required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
    "The download directory for the results,  for example: '-p /data/share/fjogl/relations_test/'. Must be a valid directory.", required=True)

args = parser.parse_args()

# Check arguments
if not os.path.isdir(args.path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it")

if args.download_all and args.ids is not None:
    raise ValueError("'-a' cannot be used together with '-i'")
    
if not args.download_all and args.ids is None:
    raise ValueError("Either '-a' or '-i' must be used")

# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()
RestAPI = VhhRestApi(config=configuration_instance)

videos_list = RestAPI.getListofVideos()

# Get ids
if args.download_all:
    ids = [video.id for video in videos_list]
else:
    ids = args.ids

# Download
for id in ids:
    data = RestAPI.getOverscans(id)
    #print(data)

    if data is None:
        print(f"Film {id} has no overscan annotations. No files will be generated.")
        continue

    path = os.path.join(args.path, f"overscans_{id}.json")
    with open(path, 'w') as file:
        json.dump(data, file)

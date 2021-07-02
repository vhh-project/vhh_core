# %%
import os
print(os.getcwd())
os.chdir("..")

from VhhRestApi import VhhRestApi
from Configuration import Configuration
import Utils
import argparse, os
import pandas as pd
import matplotlib.pyplot as plt

config_file = "../config/CORE/config.yaml"
dpi = 100

os.chdir("Develop")

#
# ARGUMENT PARSING
#

''' parser = argparse.ArgumentParser(description="Create video statsitics")
# This is a required parameter
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-p', '--path', dest='path', help =
"The download directory for the results,  for example: '-p /data/share/USERNAME/stats/'. Must be a valid directory.", required=True)
args = parser.parse_args()

if not os.path.isdir(args.path):
    raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it") '''

# Create RestAPI
configuration_instance = Configuration(config_file=config_file)
configuration_instance.loadConfig()

# Set download path to specified path
#path = args.path
path = "/data/share/fjogl/stats"

configuration_instance.video_download_path = path

RestAPI = VhhRestApi(config=configuration_instance)

# Get id of all videos
shot_data = []
videos_list = RestAPI.getListofVideos()
for video in videos_list:
    if video.processed_flag:
        shot_data.append(RestAPI.getAutomaticResults(video.id))

# Right now shot data is a list of lists, make just a list
shot_data_flat = [item for sublist in shot_data for item in sublist]

df = pd.DataFrame(shot_data_flat)
print(df)

def store_image(name):
        file_path = os.path.join(path, name)
        file_path_png = Utils.make_filepath_unique(file_path, ".png")
        file_path_pdf = Utils.make_filepath_unique(file_path, ".pdf")

        plt.savefig(file_path_png, dpi=dpi)
        plt.savefig(file_path_pdf, dpi=dpi)
        plt.clf()


ax = df['shotType'].value_counts().plot(kind='bar',
                                    figsize=(14,8),
                                    title="Number of ShotType")
store_image("shottype")

ax = df['cameraMovement'].value_counts().plot(kind='bar',
                                    figsize=(14,8),
                                    title="Number of CameraMovements")
store_image("cameramovemetn")


# %%

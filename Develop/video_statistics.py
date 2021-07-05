from VhhRestApi import VhhRestApi
from Configuration import Configuration
import Utils
import argparse, os
import pandas as pd
import matplotlib.pyplot as plt
import statistics

"""
Computes and visualizes the annotation data.
For more details on the parameters please call this script with the parameter '-h'
Needs to be run from INSIDE the Develop directory
"""

config_file = "../config/CORE/config.yaml"
dpi = 300

# These parameters inflluence the x-limit of the correspond plots
length_of_a_video_max_frames = 50000
shot_length_max_frames = 1000
number_shots_max_shots = 500

#
# DEFINITIONS
#

def add_statistics(data):
    """
    Compute average, median and standard deviation and return it as a nicely formatted string

    :param data: The data for which the statistics should be computed
    """

    if len(data) == 1:
        return "Avg: {0}".format(data[0])
    avg = round(statistics.mean(data))
    med = round(statistics.median(data))
    std = round(statistics.stdev(data))
    return "Avg: {0}, Med: {1}, Std: {2}".format(avg, med, std)

def initialize_image(title_string):
    """
    Call this everytime before you start making the illustration.

    :param title_string: The title of the image
    """

    # Source TeX: https://stackoverflow.com/questions/13132194/type-1-fonts-with-log-graphs
    #plt.rcParams['text.usetex'] = True
    fig = plt.figure()

    ax = plt.gca()
    ax.set_title(title_string)

def store_image(name):
    """
    Stores a matplotlib plot as PDF and PNG. Does not override files with the same name.

    :param name: path and name for the file, for example: /data/share/USERNAME/stats/image
    """

    file_path = os.path.join(path, name)
    file_path_png = Utils.make_filepath_unique(file_path, ".png")
    file_path_pdf = Utils.make_filepath_unique(file_path, ".pdf")
    plt.savefig(file_path_png, dpi=dpi)
    plt.savefig(file_path_pdf, dpi=dpi)
    #plt.show()
    plt.close()

def plot_shottypes(df):
    initialize_image("Number of shot types")
    ax = df['shotType'].value_counts().plot(kind='bar',
                                        figsize=(14,8))                 
    plt.xlabel("Shot type")
    plt.ylabel("Number")
    store_image("shottype")

def plot_camera_movement(df):
    initialize_image("Number of camera movements")
    ax = df['cameraMovement'].value_counts().plot(kind='bar',
                                        figsize=(14,8))
    plt.xlabel("Camera movement")
    plt.ylabel("Number")
    store_image("camera_movement")

def plot_shot_length(data, title, filename, n_bins = 200):
    """
    This is a helper function, creates and stores the plots of shot length

    :param data: The shot length data
    :param title: Title of the image
    :param filename: The filename and path, for example /data/share/USERNAME/stats/image
    :param n_bins: Number of bins used in the histogram
    """

    initialize_image(title)
    n, bins, patches = plt.hist(data, n_bins, density=False, facecolor='g', alpha=0.75)
    plt.xlabel("Shot length (in frames)")
    plt.ylabel("Number")
    store_image(filename)

def plot_shot_lengths(df, shot_types, camera_movements):
    shot_length = (df['outPoint']-df['inPoint']).to_frame()
    shot_length.columns = ["length"] 
    shot_length_short = shot_length[shot_length["length"] < shot_length_max_frames]
    plot_shot_length(shot_length, "Shot length \n{0}".format(add_statistics(shot_length['length'])), "shotlength")
    plot_shot_length(shot_length_short, "Shot length (shots with < {0} frames) \n{1}".format(shot_length_max_frames, add_statistics(shot_length_short['length'])), 
    "shotlength_{0}".format(shot_length_max_frames))

    # Plot the shot length for each shot type  
    for shot_type in shot_types:
        df_only_some =  df.loc[df['shotType'] == shot_type]
        shot_length = (df_only_some['outPoint']-df_only_some['inPoint']).to_frame()
        shot_length.columns = ["length"]
        shot_length_short = shot_length[shot_length["length"] < shot_length_max_frames]
        plot_shot_length(shot_length_short, "Shot length (shots with < {0} frames, only {1} shot type)\n{2}".format(shot_length_max_frames, shot_type, add_statistics(shot_length_short['length'])), 
        "shotlength_{0}_shottype{1}".format(shot_length_max_frames, shot_type))

    # Plot the shot length for each camera movement
    for camera_movement in camera_movements:
        df_only_some =  df.loc[df['cameraMovement'] == camera_movement]
        shot_length = (df_only_some['outPoint']-df_only_some['inPoint']).to_frame()
        shot_length.columns = ["length"]
        shot_length_short = shot_length[shot_length["length"] < shot_length_max_frames]
        plot_shot_length(shot_length_short, "Shot length (shots with < {0} frames, only {1} camera movement)\n{2}".format(shot_length_max_frames, camera_movement, add_statistics(shot_length_short['length'])), 
        "shotlength_{0}_cameramovement{1}".format(shot_length_max_frames, camera_movement))

def plot_nr_shots(number_shots):
    initialize_image("Number of shots in a video\n{0}".format(add_statistics(number_shots)))
    n, bins, patches = plt.hist(number_shots, 50, density=False, facecolor='g', alpha=0.75)
    plt.xlabel("Number of shots")
    plt.ylabel("Number")
    store_image("numbershots")

    # Also plot nr of shots for videos with less than number_shots_max_shots shots
    number_shots_reduced = [x for x in number_shots if x < number_shots_max_shots]
    initialize_image("Number of shots in a video (videos with < {0} shots)\n{1}".format(number_shots_max_shots, add_statistics(number_shots_reduced)))
    n, bins, patches = plt.hist(number_shots_reduced, 50, density=False, facecolor='g', alpha=0.75)
    plt.xlabel("Number of shots")
    plt.ylabel("Number")
    store_image("numbershots_{0}".format(number_shots_max_shots))

def plot_length(video_lengths, x_label):
    initialize_image("Length of a video\n{0}".format(add_statistics(video_lengths)))
    n, bins, patches = plt.hist(video_lengths, 50, density=False, facecolor='g', alpha=0.75)
    plt.xlabel(x_label)
    plt.ylabel("Number")
    store_image("videolength")

def plot_length_upper_bounded(video_lengths, x_label, upper_bound):
    # Also plot video length for videos with less than length_of_a_video_max_frames frames
    video_lengths_changed = [x for x in video_lengths if x < upper_bound]
    initialize_image("Length of a video (videos with < {0} frames)\n{1}".format(upper_bound, add_statistics(video_lengths_changed)))
    n, bins, patches = plt.hist(video_lengths_changed, 50, density=False, facecolor='g', alpha=0.75)
    plt.xlabel(x_label)
    plt.ylabel("Number")
    store_image("videolength_{0}".format(upper_bound))


#
# MAIN
#

def main():

#
# ARGUMENT PARSING
#

    parser = argparse.ArgumentParser(description="Create video statistics")
    parser.add_argument('-i', '--id', nargs='+', dest = "ids", type=int, help = 
"Specify ids of videos for which you want to create the statistics, for example: '-i 8213 8214'. Note that some statistics only make sense for a large number of videos.")


    # This is a required parameter
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-p', '--path', dest='path', help =
    "The download directory for the results,  for example: '-p /data/share/USERNAME/stats/'. Must be a valid directory.", required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        raise ValueError("path must point to a valid directory. Call this script with the '-h' parameter to get information on how to run it") 

    ids = []
    if args.ids is not None:
        ids = args.ids

#
# DATA LOADING AND PREPARING
#

    # Create RestAPI
    configuration_instance = Configuration(config_file=config_file)
    configuration_instance.loadConfig()

    # Set download path to specified path
    global path
    path = args.path

    configuration_instance.video_download_path = path

    RestAPI = VhhRestApi(config=configuration_instance)

    # Get id of all videos
    shot_data = []
    video_lengths = []
    number_shots = []

    videos_list = RestAPI.getListofVideos()
    for video in videos_list:
        if video.processed_flag:
            if ids == [] or video.id in ids:
                data_for_video = RestAPI.getAutomaticResults(video.id)
                shot_data.append(data_for_video)
                video_lengths.append(data_for_video[-1]['outPoint'])
                number_shots.append(len(data_for_video))

    # Right now shot data is a list of lists, make just a list
    shot_data_flat = [item for sublist in shot_data for item in sublist]

    df = pd.DataFrame(shot_data_flat)

    shot_types = df.shotType.unique()
    camera_movements = df.cameraMovement.unique()

#
# PLOT
#

    plot_nr_shots(number_shots)
    plot_length(video_lengths, "Length (in frames)")
    plot_length_upper_bounded(video_lengths, "Length (in frames)", length_of_a_video_max_frames)

    video_lengths_in_minutes = [i / (24.0*60) for i in video_lengths]

    plot_length(video_lengths_in_minutes, "Length (in minutes, assuming 24fps)")

    plot_shot_lengths(df, shot_types, camera_movements)
    plot_shottypes(df)
    plot_camera_movement(df)

if __name__ == "__main__":
    main()
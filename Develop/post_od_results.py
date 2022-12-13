from MainController import MainController
import sys, os
"""
    Manually uploads object detection json files to VHH-MMSI

    Run with python Develop/post_od_results.py FILENAME
    where FILENAME is the result you want to post, for example "8213.json"
"""

main_instance = MainController()
filename = sys.argv[1]

api = main_instance.get_rest_api()
path = os.path.join(main_instance.get_config().results_root_dir, "core", "OBA", filename)

api.postOBAResults([path])

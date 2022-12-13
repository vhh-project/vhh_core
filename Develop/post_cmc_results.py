from ftplib import all_errors
from MainController import MainController
import sys, os
"""
    Manually uploads camera movements classification json files to VHH-MMSI

    Run with python Develop/post_cmc_results.py FILENAME
    where FILENAME is the result you want to post, for example "8213.json"
"""

main_instance = MainController()
filename = sys.argv[1]

api = main_instance.get_rest_api()
path = os.path.join(main_instance.get_config().results_root_dir, "core", "TBA", filename)
api.postCMCResults([path])

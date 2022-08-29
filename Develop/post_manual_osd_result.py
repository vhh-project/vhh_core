"""
Pushes the result of manual OSD annotations to VhhMMSI
Run with
    python Develop/push_manual_os_result.py $PATH
    where $path is a path to a folder containing OSD annotations that look like VID-overscan_annotations.json (e.g. 8427-overscan_annotations.json)

If an annotation file contains multiple "frame-window" we will use the first.
"""

import os
import json
import argparse
import glob

from MainController import MainController

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args  = parser.parse_args()

    assert os.path.isdir(args.path)

    annotations_path = glob.glob(os.path.join(args.path, "*-overscan_annotations.json"))

    osd_data = []
    print(f"Found {len(annotations_path)} annotations")
    for path in annotations_path:
        with open(path) as file:
            annotation = json.load(file)

        for frame_annotation in annotation:
            width = frame_annotation["meta_info"]["size"]["width"]
            height = frame_annotation["meta_info"]["size"]["height"]

            frame_windows = list(filter(lambda region: "frame_window" in region["tags"], frame_annotation["regions"]))
            if len(frame_windows) == 1:
                break

        vid = int(os.path.split(path)[-1].split('-')[0])
        frame_window = frame_windows[0]

        # Collect x and y coordinates and normalize them
        list_x = list(map(lambda point: point["x"] / width, frame_window["points"]))
        list_y = list(map(lambda point: point["y"] / height, frame_window["points"]))

        left = min(list_x)
        right = max(list_x)
        top = min(list_y)
        bottom = max(list_y)

        osd_data.append({
                "vid": vid,
                "left": left,
                "right": right,
                "top": top,
                "bottom": bottom
            })

    # Post data to VhhMMSI
    main_instance = MainController()
    api = main_instance.get_rest_api()
    api.postOSDresults(osd_data)
    

if __name__ == "__main__":
    main()

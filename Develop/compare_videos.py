"""
Takes two videos and puts them side by side making it easier to spot differences.
The videos should have the same width and height.
Written to compare YOLOv3 with YOLOv5.
"""

import cv2
import numpy as np
from PIL import Image


# def resize(img, w, h, fill_color=(0, 0, 0, 0)):
#     print(img)
#     x, y, _ = img.shape
#     new_img = Image.new('RGBA', (h, w), fill_color)
#     new_img.paste(img, (int((w - x) / 2), int((h - y) / 2)))
#     return new_img

def main(video1_path, video2_path, video1_info, video2_info, output_path):
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    out, fourcc = None, None
    shape1, shape2, combined_shape = None, None, None
    frame1, frame2 = None, None

    # Merge videos
    for iter in __import__("itertools").count():
        print("\rWritten {0} frames".format(iter), end="")

        ret1, frame1_raw = cap1.read()
        ret2, frame2_raw = cap2.read()

        # Stop if both of the videos have ended
        if not ret1 and not ret2:
            print(ret1, ret2)
            break

        if ret1:
            frame1 = cv2.resize(frame1_raw, None, fx = 0.5, fy = 0.5, interpolation = cv2.INTER_CUBIC)
            if shape1 is None:
                shape1 = frame1.shape

        if ret2:
            frame2 = cv2.resize(frame2_raw, None, fx = 0.5, fy = 0.5, interpolation = cv2.INTER_CUBIC)
            if shape2 is None:
                shape2 = frame2.shape

        if combined_shape is None:
            if shape1[2] != shape2[2]:
                print("WARNING: Do not support comparing black and white to colored videos.")
                return
            combined_shape = (max(shape1[0], shape2[0]), max(shape1[1], shape2[1]))

        # frame1 = resize(frame1, combined_shape[0], combined_shape[1])
        # frame2 = resize(frame1, combined_shape[0], combined_shape[1])
        # print("after", frame1.shape, frame2.shape)

        

        # Resize image, only if it has not been resized before
        frame1 = cv2.resize(frame1, combined_shape)
        frame2 = cv2.resize(frame2, combined_shape)


        
        cv2.putText(frame1, video1_info, (20, frame1.shape[0]- 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 0), 2)
        cv2.putText(frame2, video2_info, (20, frame1.shape[0]- 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 0), 2)

        combined_frame = np.hstack([frame1, frame2])

        if out is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 24, (combined_frame.shape[1], combined_frame.shape[0]))

        out.write(combined_frame)

    out.release()
    

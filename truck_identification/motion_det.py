import cv2
import time
import os
from datetime import datetime

feed_name = os.path.abspath("video2.mkv")

def defineMkvFeed(camera_path):
    cap = cv2.VideoCapture(camera_path)
    frame_total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    return cap

if __name__ == '__main__':

    cap = defineMkvFeed(feed_name)

    # Video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_number = 0

    init_time = datetime.now()
    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_number += 1

            cap.set(cv2.CAP_PROP_FPS, 24)
            y = 30
            cv2.putText(frame, f"Frame: {frame_number}/{total_frames}", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(frame, f"Video FPS: {video_fps:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
          

            cv2.imshow("Video Visualization", frame)

            # Press q to quit; ESC also exits
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:
                break

    
        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print("Exception occured")


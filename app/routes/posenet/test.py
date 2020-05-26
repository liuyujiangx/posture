import cv2 as cv
import numpy as np

from app import app


class Pose():
    def pose(self,url,acc=0.9):
        BODY_PARTS = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                      "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                      "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                      "LEye": 15, "REar": 16, "LEar": 17, "Background": 18}

        POSE_PAIRS = [["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                      ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                      ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                      ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                      ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"]]
        inWidth = 368
        inHeight = 368
        net = cv.dnn.readNetFromTensorflow(app.config['UP_DIR']+"graph_opt.pb")

        img = cv.imread(url)
        net.setInput(
            cv.dnn.blobFromImage(img, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        out = net.forward()
        out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

        assert (len(BODY_PARTS) == out.shape[1])

        points = []
        for i in range(len(BODY_PARTS)):
            # Slice heatmap of corresponging body's part.
            heatMap = out[0, i, :, :]

            # Originally, we try to find all the local maximums. To simplify a sample
            # we just find a global one. However only a single pose at the same time
            # could be detected this way.
            _, conf, _, point = cv.minMaxLoc(heatMap)
            x = (inWidth * point[0]) / out.shape[3]
            y = (inHeight * point[1]) / out.shape[2]
            # Add a point if it's confidence is higher than threshold.
            points.append((int(x), int(y)) if conf > acc else None)
        paintPose = []
        for pair in POSE_PAIRS:
            partFrom = pair[0]
            partTo = pair[1]
            assert (partFrom in BODY_PARTS)
            assert (partTo in BODY_PARTS)

            idFrom = BODY_PARTS[partFrom]
            idTo = BODY_PARTS[partTo]

            if points[idFrom] and points[idTo]:
                paintPose.append([idFrom, idTo])
                cv.line(img, points[idFrom], points[idTo], (0, 255, 0), 3)
                cv.ellipse(img, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
                cv.ellipse(img, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
        # print(list(map(list,points)))

        return {'arr':points,'pose':paintPose}

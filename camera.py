import dlib
from imutils import face_utils
import pickle
import cv2
import mpmath
import numpy as np
import csv

dlib_path = "dlibb/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(dlib_path)


class VideoCamera(object):

    def __init__(self):
        self.Expression = []
        self.return_list = []
        self.frame = -1
        self.video = cv2.VideoCapture(0)
        # self.video = cv2.VideoCapture("output.avi")
        # self.video.set(cv2.CAP_PROP_FPS, 5)

    def destroy(self):

        self.video.release()
        cv2.destroyAllWindows()
        # self.endd = time.time()
        # print(self.endd)
        # S =  self.start_time - self.endd
        # print(S)

    def get_frame(self):

        pickle_in = open("New_testing_dlib_normalized.pickle", "rb")

        model = pickle.load(pickle_in)
        while(self.video.isOpened()) :
            self.frame += 1
            ret, frame = self.video.read()
            if ret is True:
                if self.frame % 5 == 0:
                    # print(str(self.frame)+" frame")
                    #ret, frame = self.video.read()
                    # if ret == True:
                    self.frame+=1
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    file = open("Expressions.csv", "w")
                    face = detector(gray,0)
                    # print("Number of Faces {}".format(len(face)))
                    my_list = []
                    count_interested= 0
                    count_bore  =0
                    count_neutral =0
                    for (J, rect) in enumerate(face):
                        shap = predictor(frame, rect)
                        xlist = []
                        ylist = []
                        shap = face_utils.shape_to_np(shap)
                        Centre = (shap[30])
                        centre_x = Centre[0]
                        centre_y = Centre[1]
                        shap = shap[18:68]
                        for i in shap:
                            xlist.append(i[0])
                            ylist.append(i[1])
                        forx = []
                        fory = []
                        for x in xlist:
                            forx.append((x - centre_x) ** 2)
                        for y in ylist:
                            fory.append((y - centre_y) ** 2)
                        listsum = [sum(x) for x in zip(forx, fory)]
                        features = []
                        for i in listsum:
                            k = mpmath.sqrt(float(i))
                            features.append(float(k))
                        maxx = (max(features))
                        final = []
                        for i in features:
                            if (i == 0.0):
                                continue
                            F = i / maxx
                            final.append(F)
                        # print(final)
                        numpy_array = np.array(final)
                        prediction = model.predict([numpy_array])[0]
                        # print(prediction)
                        # print("done")
                        (x, y, w, h) = face_utils.rect_to_bb(rect)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        # display the image and the prediction
                        cv2.putText(frame, prediction, (x-7, y-6), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                    (0, 255, 0), 2)
                        cv2.circle(frame, (centre_x, centre_y), 1, (0, 0, 0), 10)
                        for (x, y) in shap:
                            cv2.circle(frame, (x, y), 1, (0, 0, 255), 2)
                            cv2.line(frame,(centre_x,centre_y),(x,y),(0,255,1) )
                        cv2.waitKey(100)
                        if prediction == "INTERESTED":
                            count_interested += 1
                            # self.Expression.append(1)

                        elif prediction == "BORE":
                            count_bore +=1
                        else:
                            count_neutral += 1

                        ret, jpeg = cv2.imencode('.jpg', frame)
                        my_list.append(jpeg.tobytes)

                    if (count_interested > count_bore) and (count_interested > count_neutral):
                        self.Expression.append(1)

                    elif (count_bore > count_interested) and (count_bore > count_neutral):
                        self.Expression.append(-1)
                    else:
                        self.Expression.append(0)

                    with file:
                     writter = csv.writer(file)
                     writter.writerow(self.Expression)
                    return (my_list)
            else:
                break

# from tools.converters.local.kit import toolKit as localConvertersTools
import numpy as np
import imutils
import cv2
import os
from tools.converters.local.kit import toolKit as localConvertersTools

dataPath = ".temp"
idPath = ".temp/face/{}_face.xml"
cascade = "assets/visual/haarcascade/haarcascade_frontalface_default.xml"
userList = os.listdir(dataPath)
user = ""
faceClassifier = cv2.CascadeClassifier(cascade)


class AmyCamera:
    def __init__():
        pass

    def recognize_camera():
        camera_index = 0
        camera_list = []
        while True:
            cap = cv2.VideoCapture(camera_index)
            if not cap.read()[0]:
                break
            else:
                camera_list.append(camera_index)
                cap.release()
            camera_index += 1

        return len(camera_list)

    def show_camera():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow("frame", frame)
            if cv2.waitKey(5) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def show_all_cameras():
        # get the index of all connected cameras
        camera_indexes = []
        for index in range(10):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                camera_indexes.append(index)
            cap.release()

        # print the index of each connected camera
        print(f"{len(camera_indexes)} cameras found!")
        for index in camera_indexes:
            print(f"Camera {index} is connected.")

        # open a window to show all the connected cameras
        cv2.namedWindow("Cameras Monitoring", cv2.WINDOW_NORMAL)

        # start reading frames from the cameras and show them in the same window
        while True:
            # initialize an empty list to store the frames from all cameras
            frames = []
            for index in camera_indexes:
                cap = cv2.VideoCapture(index)
                ret, frame = cap.read()
                cap.release()

                # add the frame to the list of frames
                if ret:
                    frames.append(frame)

            # if there are frames, stack them horizontally and show them in the window
            if len(frames) > 0:
                stacked_frames = cv2.hconcat(frames)
                cv2.imshow("Cameras Monitoring", stacked_frames)

            # exit the window if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()


class FacialRecognizer:
    def __init__():
        pass

    def facial_recorder(userPath):
        global faceClassifier
        imgCount = 0
        cap = cv2.VideoCapture(0)
        if not os.listdir(userPath):
            while True:
                ret, frame = cap.read()
                if ret == False:
                    break
                frame = imutils.resize(frame, width=320)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                auxFrame = frame.copy()
                faceClassif = faceClassifier.detectMultiScale(gray, 1.1, 1)
                for x, y, w, h in faceClassif:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    face = auxFrame[y : y + h, x : x + w]
                    face = cv2.resize(face, (450, 450), interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(userPath + "/face_{}.jpg".format(imgCount), face)
                    imgCount += 1

                cv2.imshow("frame", frame)
                if cv2.waitKey(5) == 27 or imgCount >= 450:
                    break
            cap.release()
            cv2.destroyAllWindows()
        return FacialRecognizer.facial_encoder()

    def facial_encoder():
        global user
        global dataPath
        global idPath
        facesData = []
        labels = []
        personPath = dataPath + "/face/" + user

        for filename in os.listdir(personPath):
            facesData.append(cv2.imread(personPath + "/" + filename, 0))
            image = cv2.imread(personPath + "/" + filename, 0)
            labels.append(0)
        print("Training...")
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.train(facesData, np.array(labels))
        print("Saving File...")
        face_recognizer.write(idPath.format(user))
        cv2.destroyAllWindows()
        rut = ".temp/{}_face.zip".format(user)
        localConvertersTools.zipper([(".temp/face/{}_face.xml".format(user), rut)])
        return rut

    def pip_faces(user):  # NOT FINISHED
        global faceClassifier
        global userList
        cap = cv2.VideoCapture(0)
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.read(
            "/visual/faceID/{}_faceLock.xml".format(user)
        )  # se debe cambiar por documento general extraido de la base de datos

        while True:
            ret, frame = cap.read()
            if ret == False:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            auxFrame = gray.copy()
            faceClassif = faceClassifier.detectMultiScale(gray, 1.1, 1)
            for x, y, w, h in faceClassif:
                face = auxFrame[y : y + h, x : x + w]
                face = cv2.resize(face, (150, 150), interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(face)

                if result[1] < 60:
                    cv2.putText(
                        frame,
                        "{}".format(userList[result[0]]),
                        (x, y - 25),
                        2,
                        1.1,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    cv2.putText(
                        frame,
                        "Desconocido",
                        (x, y - 20),
                        2,
                        0.8,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.imshow("frame", frame)
            if cv2.waitKey(5) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
        return

    def face_locker(user):
        global faceClassifier
        global userList
        global dataPath
        path = dataPath + "/{}_face.xml".format(user)
        cap = cv2.VideoCapture(0)
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.read(path)
        key = 0

        while True:
            ret, frame = cap.read()
            if ret == False:
                return False
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            auxFrame = gray.copy()
            faceClassif = faceClassifier.detectMultiScale(gray, 1.1, 1)
            for x, y, w, h in faceClassif:
                face = auxFrame[y : y + h, x : x + w]
                face = cv2.resize(face, (450, 450), interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(face)

                if result[1] < 60:
                    cv2.putText(
                        frame,
                        "{}".format(user),
                        (x, y - 25),
                        2,
                        1.1,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    key = 1
                else:
                    cv2.putText(
                        frame,
                        "Desconocido",
                        (x, y - 20),
                        2,
                        0.8,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    pass
            cv2.imshow("frame", frame)
            if key == 1:
                cap.release()
                cv2.destroyAllWindows()
                return True
            if cv2.waitKey(5) == 27:
                cap.release()
                cv2.destroyAllWindows()
                return False

    def run(userName, typ):
        global dataPath
        global user
        global idPath
        user = userName
        userPath = dataPath + "/face/" + user
        if typ == 0:
            os.makedirs(userPath)
            print("Directorio temporal de usuario Creado.")
            return FacialRecognizer.facial_recorder(userPath)
        elif typ == 1:
            key = FacialRecognizer.face_locker(userName)
            if key == True:
                return True
            elif key == False:
                return False


if __name__ == "__main__":
    AmyCamera.show_all_cameras()

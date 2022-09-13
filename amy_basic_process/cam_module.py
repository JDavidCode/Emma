import cv2
import os
import imutils
import numpy as np

dataPath = 'c:/Users/Juan/Documents/AmyAssistant/visual/personsData'
userList = os.listdir(dataPath)
cascade = 'c:/Users/Juan/Documents/AmyAssistant/visual/haarcascade/haarcascade_frontalface_default.xml'
user = ''

faceClassifier = cv2.CascadeClassifier(cascade)


class camera:
    def __init__():
        pass

    def camInit():
        cap = cv2.VideoCapture(0)
        return cap

    def showCamera():
        cap = camera.camInit()
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imshow('frame', frame)
            if cv2.waitKey(5) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()


class facialRecognizer:

    def __init__():
        pass

    def userPather(userName):
        global dataPath
        global user
        userPath = dataPath + '/' + user
        if not os.path.exists(userPath):
            os.makedirs(userPath)
            print('Directorio de usuario Creado.')
            facialRecognizer.facialRecorder(userPath)
        else:
            facialRecognizer.faceLock()

    def facialRecorder(userPath):
        global faceClassifier
        imgCount = 0
        cap = camera.camInit()
        if not os.listdir(userPath):
            while True:
                ret, frame = cap.read()
                if ret == False:
                    break
                frame = imutils.resize(frame, width=320)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                auxFrame = frame.copy()
                faceClassif = faceClassifier.detectMultiScale(gray, 1.1, 1)
                for (x, y, w, h) in faceClassif:
                    cv2.rectangle(frame, (x, y), (x+w, y+h),
                                  (255, 255, 255), 2)
                    face = auxFrame[y:y + h, x:x+w]
                    face = cv2.resize(face, (300, 300),
                                      interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(
                        userPath + '/face_{}.jpg'.format(imgCount), face)
                    imgCount += 1

                cv2.imshow('frame', frame)
                if cv2.waitKey(5) == 27 or imgCount >= 450:
                    break
            cap.release()
            cv2.destroyAllWindows()
        facialRecognizer.faceCoder()

    def faceCoder():
        global user
        global dataPath
        facesData = []
        labels = []
        personPath = dataPath + '/' + user

        for filename in os.listdir(personPath):
            facesData.append(cv2.imread(personPath + '/' + filename, 0))
            image = cv2.imread(personPath+'/'+filename, 0)
            labels.append(0)
        print('Training...')
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.train(facesData, np.array(labels))
        print('Saving File...')
        face_recognizer.write(
            'c:/Users/Juan/Documents/AmyAssistant/visual/faceID/{}_faceLock.xml'.format(user))
        cv2.destroyAllWindows()

        facialRecognizer.faceLock()

    def faceLock():
        global user
        global faceClassifier
        global userList
        cap = camera.camInit()
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_recognizer.read(
            'c:/Users/Juan/Documents/AmyAssistant/visual/faceID/{}_faceLock.xml'.format(user))

        while True:
            ret, frame = cap.read()
            if ret == False:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            auxFrame = gray.copy()
            faceClassif = faceClassifier.detectMultiScale(gray, 1.1, 1)
            for (x, y, w, h) in faceClassif:
                face = auxFrame[y:y+h, x:x+w]
                face = cv2.resize(face, (150, 150),
                                  interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(face)

                if result[1] < 60:
                    cv2.putText(frame, '{}'.format(
                        userList[result[0]]), (x, y-25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                else:
                    cv2.putText(frame, 'Desconocido', (x, y-20), 2,
                                0.8, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.imshow('frame', frame)
            if cv2.waitKey(5) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    facialRecognizer.userPather(input('Name: '))

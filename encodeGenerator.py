#Here we generede all code that we need

import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendacerealtime-cf1e2-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-cf1e2.appspot.com"
})

##Encoding Generator
#Importing the student images into a list
folderPath= 'Images/'
pathList= os.listdir(folderPath) #We obtein ['1.png','2.png']
imgList= []
studentIds= []
for path in pathList:
    imgmode= cv2.resize(cv2.imread(os.path.join(folderPath, path)), (405, 633),interpolation= cv2.INTER_CUBIC)
    imgList.append(imgmode)#we join these and add to the list
    studentIds.append(os.path.splitext(path)[0])
    #print(os.path.splitext(path)[0])
    #studentIds.append(path.split(".")[0])
    #print(path.split(".")[0])

    ##Upload Images to Database
    fileName= os.path.join(folderPath, path)
    bucket= storage.bucket() #We create the bucket
    blob= bucket.blob(fileName)
    blob.upload_from_filename(fileName)

#print(studentIds)


def findEncodings(imagesList):
    encodeList= []
    for img in imagesList:
        img= cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Changing because cv2 use BGR and the library use RGB
        try:
            encode= face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError as e:
            print(e)

    return encodeList

print("Encoding Started ...")
encodeListKnown= findEncodings(imgList)
encodeListKnownWithIds= [encodeListKnown, studentIds]
#print( encodeListKnownWithIds[0][0]+ "  and ID: "+ encodeListKnownWithIds[1][0])
print("Encoding Complete")

file= open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
print("File Saved")
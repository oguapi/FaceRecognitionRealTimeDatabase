#In this app the students will we identify by id and not for the name

import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendacerealtime-cf1e2-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-cf1e2.appspot.com"
})

#For the image
bucket= storage.bucket()

##WEBCAM
cap= cv2.VideoCapture(0)
#We specify the width we need for the graphics because the graphics was based on these dimensions
cap.set(3, 640)
#And the height too
cap.set(4, 480)

##IMPORT GRAPHICS
imgBackground= cv2.imread('Resources/background.png')

#Importing the modes images into a list
folderModesPath= 'Resources/Modes/'
modePathList= os.listdir(folderModesPath) #We obtein ['1.png','2.png']
imgModeList= []
for path in modePathList:
    imgmode=cv2.imread(os.path.join(folderModesPath, path))
    imgmode= cv2.resize(imgmode, (405, 633),interpolation= cv2.INTER_CUBIC)
    imgModeList.append(imgmode)#we join these and add to the list
#print(len(imgModeList))
#cv2.resize(cv2.imread(os.path.join(folderModesPath)), (414, 633),interpolation= cv2.INTER_CUBIC)

##FACE RECOGNITION
#Load the encoding file
print("Loading encoding file ...")
file= open('EncodeFile.p','rb')
encodeListKnownWithIds= pickle.load(file)
file.close
encodeListKnown, studentIds= encodeListKnownWithIds
#print(studentIds)
print("Encode file Loaded")

modeType=0
counter= 0 #When the face is detected we only need to download the information in the first frame
id= -1     #Because we verificate an add 1 to counter
imgStudent= []

while True:
    #this is the Standard, you can say is the boilerplates template code for running a webcam
    success, img= cap.read()

    imgS= cv2.resize(img,(0,0),None, 0.25, 0.25) #New images to comparate
    imgS= cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB) #Changing because cv2 use BGR and the library use RGB

    faceCurFrame= face_recognition.face_locations(imgS)
    encodeCurFrame= face_recognition.face_encodings(imgS, faceCurFrame)

    #Merge the background and the webcam video, we tell the height and width
    imgBackground[176:176 + 480, 135:135 + 640]= img
    imgBackground[70:70 + 633, 908:908 + 405]= imgModeList[modeType] #Adding the modes to background
    
    if faceCurFrame:
        for encodeFace, faceloc in zip(encodeCurFrame, faceCurFrame):
            matches= face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis= face_recognition.face_distance(encodeListKnown,encodeFace)
            #print("matches", matches) #Result for my face [True, False, False]
            #print("faceDis", faceDis) #[0.5096803  1.000487   0.82014385]

            matchIndex= np.argmin(faceDis)
            #print("Match Index", matchIndex) #For my the result es value 0

            if matches[matchIndex]:
                #print("Known Face Detected")
                #print(studentIds[matchIndex])
                y1, x2, y2, x1= faceloc
                y1, x2, y2, x1= y1*4, x2*4, y2*4, x1*4 #Multiple by four because we reduce the size of the image
                bbox= 150 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground= cvzone.cornerRect(imgBackground, bbox, rt=0)
                id= studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))#Look better when the code loading the information
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter= 1
                    modeType=1 #Because we need to update the mode which will go over here
        if counter != 0:
            if counter== 1:
                #We download the information, get the data
                studenInfo= db.reference(f'Students/{id}').get() #We pass the id of the student detected
                print(studenInfo)
                #Get the Image from the storage
                blob= bucket.get_blob(f'Images/{id}.jpg')
                array= np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent= cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                #Update data of attendance
                dateTimeObject= datetime.strptime(studenInfo['last_attendance_time'],
                                                "%Y-%m-%d %H:%M:%S") #Extrate the date time to verify if pass 30s to next attendance
                secondsElapsed= (datetime.now()-dateTimeObject).total_seconds()
                print(secondsElapsed)
                #Wait a lapse
                if secondsElapsed > 30:
                    ref= db.reference(f'Students/{id}') #With this reference we are going to send the data
                    studenInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studenInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType= 3
                    counter= 0
                    imgBackground[70:70 + 633, 908:908 + 405]= imgModeList[modeType] #Update the background
            
            #Void the overlap of the 2 modes
            if modeType != 3:
                #Chage the mode to chech
                if 15< counter <20:
                    modeType= 2
                imgBackground[70:70 + 633, 908:908 + 405]= imgModeList[modeType] #Update the background

                if counter <=15:

                    cv2.putText(imgBackground, str(studenInfo['total_attendance']),
                                (950,115),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1)
                    cv2.putText(imgBackground, str(studenInfo['major']),
                                (1090,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground, str(id), (1090,470),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground, str(studenInfo['starding']),
                                (1040,655),cv2.FONT_HERSHEY_COMPLEX,0.6,(245,0,0),1)
                    cv2.putText(imgBackground, str(studenInfo['year']),
                                (1150,655),cv2.FONT_HERSHEY_COMPLEX,0.6,(245,0,0),1)
                    cv2.putText(imgBackground, str(studenInfo['starting_year']),
                                (1240,655),cv2.FONT_HERSHEY_COMPLEX,0.6,(245,0,0),1)
                    #We need to find the width of this name to center it
                    #the center point on interest area is (1110,410)
                    (w,h),_= cv2.getTextSize(studenInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset= -w//2
                    cv2.putText(imgBackground, str(studenInfo['name']),
                                (1110+offset,410),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1) #before point (950,410)
                    
                    imgBackground[170: 170+185, 1010:1010+200]= cv2.resize(imgStudent,(200,185), interpolation=cv2.INTER_CUBIC)
            
                counter+=1

                if counter>= 20:
                    counter= 0
                    modeType= 0
                    studenInfo= []
                    imgStudent= []
                    imgBackground[70:70 + 633, 908:908 + 405]= imgModeList[modeType] #Update the background
    else:
        modeType= 0
        counter= 0

    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance", imgBackground)#Display de background
    cv2.waitKey(1)


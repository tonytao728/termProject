from cmu_112_graphics import *
from PIL import ImageTk
from PIL import Image
import numpy as np
import imutils
from imutils.video import FileVideoStream
import cv2
import mss
import time
import pytesseract
import string

def initConstants(app):
    pytesseract.pytesseract.tesseract_cmd = r"/Users/tony/tesseract/build/tesseract" 
    app.faceCascade = cv2.CascadeClassifier("resources/haarcascade_frontalface_default.xml")

    app.blue = (255, 0, 0)
    app.green = (0, 255, 0)
    app.red = (0, 0, 255)
    app.scale = 1.5
    # face size limits
    # app.faceUpperLim = 
    # app.faceLowerLim = 
    # rectangle mask
    app.recLevels = {"minH":30, "maxH":63,
                        "minS":82,"maxS":160,
                        "minV":176,"maxV":255 }
    app.recLower = np.array([app.recLevels["minH"], app.recLevels["minS"], app.recLevels["minV"]])
    app.recUpper = np.array([app.recLevels["maxH"], app.recLevels["maxS"], app.recLevels["maxV"]])
    # word mask
    app.wordMaskLevels = {"minH":0, "maxH":95,
                        "minS":0,"maxS":0,
                        "minV":133,"maxV":255 }
    app.wordLower = np.array([app.wordMaskLevels["minH"], app.wordMaskLevels["minS"], app.wordMaskLevels["minV"]])
    app.wordUpper = np.array([app.wordMaskLevels["maxH"], app.wordMaskLevels["maxS"], app.wordMaskLevels["maxV"]])
    # people list
    app.people = {"sara", "liang", "tony", "tao", "karen", "li", "michael", "crotty", "kobe", "zhang"
                    "meng", "oi", "james", "chen", "jordan", "stephen", "dai", "kruthi", "thangali", "srinualnad", 
                    "ravi", "patel"}
    


def preProcess(app, frame):
    app.img = frame
    # app.dimensions = app.img.shape
    app.img = cv2.resize(app.img, (int(1920*app.scale), int(1080*app.scale)))
    app.hsvImg = cv2.cvtColor(app.img, cv2.COLOR_BGR2HSV)
    app.greyImg = cv2.cvtColor(app.img, cv2.COLOR_BGR2GRAY)
    # app.resultImg = app.img.copy()
    # detection stuff
    # masks
    app.recMask = cv2.inRange(app.hsvImg, app.recLower, app.recUpper)
    app.wordMask = cv2.inRange(app.hsvImg, app.wordLower, app.wordUpper)
    # detect the rectangle
    speakerImg = cv2.bitwise_and(app.img, app.img, mask = app.recMask)
    greySpeakerImg = cv2.cvtColor(speakerImg, cv2.COLOR_BGR2GRAY)
    blurSpeakerImg = cv2.GaussianBlur(greySpeakerImg,(7,7),0.5)
    app.cannySpeakerImg = cv2.Canny(blurSpeakerImg, 50, 50)
    # detect the words
    app.blurWordMask = cv2.GaussianBlur(app.wordMask, (7,7),0.5)
    app.cannyWordMask = cv2.Canny(app.blurWordMask, 50,50)

def appStarted(app):
    initConstants(app)
    app.running = False
    app.count = 0
    app.timerDelay = 10

def keyPressed(app,event):
    if event.key == "r":
        app.running = not app.running


def getRectangle(app):
    areaThresh = 3333*app.scale # threshold for the speaker rectangle
    contours, hierarchy = cv2.findContours(app.cannySpeakerImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > areaThresh:
            # cv2.drawContours(app.resultImg, cnt, -1, app.red, 2)
            perimeter = cv2.arcLength(cnt, True)
            points = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
            (x1, y1) = points[0][0]
            (x2, y2) = points[2][0]
            # cv2.circle(app.resultImg, (x1,y1), 4, app.blue, -1) # (x,y), radius, color, thickness (-1 means fill)
            # cv2.circle(app.resultImg, (x2,y2), 4, app.blue, -1)

def getFaces(app):
    faces = app.faceCascade.detectMultiScale(app.greyImg, scaleFactor=1.1, minNeighbors=3)
    for rec in faces:
        x, y, width, height = rec
        if 60 < width < 150:
            pass
            # cv2.putText(app.resultImg, f"size, {width}", (x,y-10), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 3, color = app.green, thickness=2)
            # cv2.rectangle(app.resultImg, (x,y), (x+width,y+height), color = app.green, thickness = 2)

def getWords(app):
    dataTable = pytesseract.image_to_data(app.cannyWordMask)
    for index, row in enumerate(dataTable.splitlines()):
        if index == 0:
            continue
        wordData = row.split()
        if wordData[-1].isalpha() and len(wordData) == 12:
            x, y, w, h, word = int(wordData[6]),int(wordData[7]),int(wordData[8]),int(wordData[9]), wordData[11]
            # if word.strip().lower() in app.people:
            # cv2.putText(app.resultImg, f"{word}", (x, y - 20),fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale = 2, color=app.red, thickness=3)
            # cv2.rectangle(app.resultImg,(x,y),(x+w,y+h), app.red, 3)

def runProgram(app):
    with mss.mss() as sct:
        frame = np.array(sct.grab(sct.monitors[2]))
        preProcess(app, frame)
        getFaces(app)
        getRectangle(app)
        getWords(app)
        # cv2.imshow("app", app.resultImg)
    
def timerFired(app):
    app.count += 1
    print(f"running...{app.count}")
    if app.running:
        runProgram(app)


def redrawAll(app, canvas):
    canvas.create_text(app.width/2, 220, text = "Press R to run app")


runApp(width = 400, height = 400) 

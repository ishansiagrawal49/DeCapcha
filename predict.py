import numpy as np
from keras.models import load_model
from PIL import ImageOps
import glob
import os
from PIL import Image
import numpy as np
from time import time as tm
import cv2

model = load_model('my_model_small.h5')
# DO NOT CHANGE THE NAME OF THIS METHOD OR ITS INPUT OUTPUT BEHAVIOR

# INPUT CONVENTION
# filenames: a list of strings containing filenames of images

# OUTPUT CONVENTION
# The method must return a numpy array (not numpy matrix or scipy matrix) and a list of strings.
# Make sure that the length of the array and the list is the same as the number of filenames that 
# were given. The evaluation code may give unexpected results if this convention is not followed.

def decaptcha( filenames ):
    width = 600
    height = 150
    percentFilterRow = 12
    percentFilterCol = 12
    errorcnt=0
    count =0
    total_count=0
    length_list = []
    final = None
    for captcha_image_file in filenames:
        
        filename = captcha_image_file

        img=cv2.imread(filename)
        im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = 127
        im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,15))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.GaussianBlur(img,(3,11),10)

        brown_lo=np.array([max(img[0,0,i]-30,0) for i in range(3)] )
        brown_hi=np.array([min(img[0,0,i]+30,255) for i in range(3)] )
        mask=cv2.inRange(img,brown_lo,brown_hi)

        im_bw[mask > 0] = 0

        #################################################################
        
        nonzero = im_bw.sum(axis=0)
        start_col=[]
        end_col=[]
        isgoing=0
        startcoltemp=-1
        for i in range(600):
            if nonzero[i]>percentFilterRow:
                if isgoing==0:
                    isgoing=1
                    startcoltemp=i
            else:
                if isgoing==1:
                    isgoing=0
                    if i-startcoltemp<percentFilterCol:
                        continue
                    end_col.append(i)
                    start_col.append(startcoltemp)
                    

        numLet = len(start_col)


        length_list.append(numLet)

        count2=0

        for i in range(numLet):
            smallImg = im_bw[:,start_col[i]:end_col[i]]
            smallImg = 255-smallImg

            im = Image.fromarray(smallImg)

            width, height = im.size

            pad = 150-width
            padding = (pad//2, 0, pad-pad//2, 0)

            img = ImageOps.expand(im, padding,fill='white')
            img = img.resize((28,28), Image.ANTIALIAS)

            img = np.asarray(img,dtype="float32").reshape((28,28,1))
            if final is None:
                final = ([img])
            else:
                final.append(img)


    final = np.array(final)

    final = final/255
    results = model.predict(final)
    results = np.argmax(results, axis = 1)
    ans = ""



    list_of_alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ref_index=0
    codes=[]

    for ele in length_list:
        ans = ""
        for index_ele in range(ele):
            ans += (list_of_alphabets[results[ref_index+index_ele]])
        ref_index+=ele
        codes.append(ans)

    numChars = np.asarray(length_list)
    return(numChars,codes)

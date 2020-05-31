import cv2 as cv
import math
def zoom(url,saveurl,color=[255,255,255,100]):

    img=cv.imread(url)
    scale=360/max(img.shape[0],img.shape[1])

    img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)
    expandx,expandy=img.shape[1],img.shape[0]
    x=(360-expandx)/2
    y=(360-expandy)/2
    img=cv.copyMakeBorder(img,int(y),int(math.ceil(y)),int(x),int(math.ceil(x)),cv.BORDER_CONSTANT,value=color)
    cv.imwrite(saveurl,img)



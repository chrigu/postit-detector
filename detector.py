import os
import cv2
import json
import urllib.request
import numpy as np

PINK_MIN = 300 / 2
PINK_MAX = 330 / 2

YELLOW_MIN = 40 / 2
YELLOW_MAX = 60 / 2


def determine_color(hue, colors):
    if PINK_MAX > hue > PINK_MIN and "pink" not in colors:
        colors["pink"] = hue
    elif YELLOW_MAX > hue > YELLOW_MIN and "yellow" not in colors:
        colors["yellow"] = hue


def find_contours_for_colour(image, hue_min, hue_max):
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = image_hsv[:, :, 0]
    print(hue_min, hue_max)
    # Filter out green postit note color
    # yellow is 90-100
    # pink is 137-150
    # green is 80-90
    hue[hue < hue_min] = 0
    hue[hue > hue_max] = 0
    hue[hue > 0] = 255
    cv2.imshow('Contours', hue)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    hue = cv2.erode(hue, None, iterations=2)
    hue = cv2.dilate(hue, None, iterations=2)

    image2, contours, hierarchy = cv2.findContours(
        hue,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )
    contours_of_interest = []
    center = [0, 0]

    if len(contours) > 0:
        contour = contours[0]
        area = cv2.contourArea(contour)
        print("area", area)

        for c in contours:
            # print("area", cv2.contourArea(c))
            # if cv2.contourArea(c) > area:
            #     area = cv2.contourArea(c)
            #     contour = c
            if cv2.contourArea(c) > 500:
                contours_of_interest.append(c)

        # m = cv2.moments(contour)
        # center = [0, 0]
        # if m['m00'] != 0:
        #     center = [m['m10'] / m['m00'], m['m01'] / m['m00']]

        # center = [int(center[0]), int(center[1])]

        cv2.drawContours(image, contours_of_interest, -1, (0, 255, 0), 3)

        cv2.imshow('Contours', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return contours_of_interest


def crop(mask, out):
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    out = out[topx:bottomx + 1, topy:bottomy + 1]

    # Show the output image
    cv2.imshow('Output', out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def imgFromUrl(url):
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    return cv2.imdecode(arr, -1) # 'Load it as it is'

def find_postits(url, update):
    # image = cv2.imread(url)
    image = imgFromUrl(url)

    height, width = image.shape[:2]
    main_image = {
        "url": url,
        "height": height,
        "width": width
    }

    update({
        "status": "imageread", 
        "mainImage": main_image
        })

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    # plt.imshow(hist, interpolation='nearest')
    # plt.show()

    update({"status": "histdone"})

    # https://stackoverflow.com/questions/47342025/how-to-detect-colored-patches-in-an-image-using-opencv
    h, s, v = cv2.split(hsv)
    ##(3) threshold the S channel using adaptive method(`THRESH_OTSU`)
    th, threshed = cv2.threshold(s, 100, 255, cv2.THRESH_OTSU|cv2.THRESH_BINARY)

    ##(4) print the thresh, and save the result
    print("Thresh : {}".format(th))
    # cv2.imshow('threshold', threshed)
    # cv2.waitKey(0)

    ##(4) find all the external contours on the threshed S
    _, cnts, _ = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    canvas  = image.copy()
    #cv2.drawContours(canvas, cnts, -1, (0,255,0), 1)

    ## sort and choose the largest contour
    cnts = sorted(cnts, key=cv2.contourArea)
    cnt = cnts[-1]

    postits = []

    for index, cnt in enumerate(cnts):
        ## approx the contour, so the get the corner points
        arclen = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * arclen, True)
        cv2.drawContours(canvas, [cnt], -1, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.drawContours(canvas, [approx], -1, (0, 0, 255), 1, cv2.LINE_AA)
        x, y, w, h = cv2.boundingRect(cnt)

        if w > 50 and h > 50:
            new_img = image[y:y+h,x:x+w]
            path = "../postit-web/uploads/{}.jpg".format(str(index))
            print(path)
            cv2.imwrite(path, new_img)

            postit = {
                "url": "{}/{}.jpg".format('http://localhost:4000', str(index)),
                "x": x,
                "y": y,
                "width": w,
                "height": h
            }

            postits.append(postit)

    return {
        "status": "done",
        "postits": postits
    }
    # cv2.imshow('detected', canvas)
    # cv2.waitKey(0)

    # cv2.destroyAllWindows()

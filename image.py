import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def to_grayscale(img):
    # (32 ,32, 1)
    img = [[sum(pixel) // 3 for pixel in line] for line in img]
    img = np.array(img)
    return img

def calc_histograma(img):
    imgflat = img.flatten()
    dic = {x:0 for x in range(0,256)}
    for pixel in imgflat:
        dic[pixel] += 1
    
    return dic

if __name__ == "__main__":
    img = cv2.imread('imgdatabase/wrecker_s_001348.png')
    aux = to_grayscale(img)
    #cv2.imshow('img', aux)
    #cv2.waitKey(0)
    #cv2.imwrite('batata.png', aux)
    histogram = calc_histograma(aux)
    print(histogram)

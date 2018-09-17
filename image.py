import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import ast
import os
import operator

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

def save_histograms(histogramas):
    with open('histograms.txt', 'a') as f:
        for i in histogramas.keys():
            w = str(i) + '#' + str(histogramas[i]) + '\n'
            f.write(w)
        f.close()

def build_all_histograms(path):
    histogramas = {}
    cont = 1
    print('Init histograms')
    for fil in os.listdir(path):
        print(fil)
        img = to_grayscale(cv2.imread(f'{path}/{fil}'))
        hist = calc_histograma(img)
        histogramas[fil] = hist
        cont += 1

    save_histograms(histogramas)
    print('Histograms saved!')
    return histogramas

import math

def normalize_hist(hist):
    hist_norm = {}
    
    for pix in hist:
        hist_norm[pix] = hist_norm.get(pix, hist[pix])
        hist_norm[pix] /= np.sum(list(hist.values()))

    return hist_norm

def euclidian_distance(v1, v2):
    return (v1 - v2)**2


def rank_images(img_hist, histograms):
    files = list(histograms.keys())
    euclidian_diff = {}
    for f in files:
        euclidian_diff[f] = euclidian_diff.get(f, 0)
        norm_img_hist = normalize_hist(img_hist)
        norm_histograms = normalize_hist(histograms[f])
        for pix_value in norm_img_hist:
            pix_distance = euclidian_distance(norm_img_hist[pix_value], norm_histograms[pix_value])
            euclidian_diff[f] += pix_distance
        euclidian_diff[f] = math.sqrt(euclidian_diff[f])
    
    euc_diff_sorted = sorted(euclidian_diff.items(), key=operator.itemgetter(1))   
    return euc_diff_sorted


if __name__ == "__main__":
    img = cv2.imread('corel1000/Africa81.jpg')
    aux = to_grayscale(img)
    
    histogram = calc_histograma(aux)
    if os.path.exists('./histograms.txt'):
        hists = {}

        with open('histograms.txt', 'r') as f:
            lines = [line.split('#') for line in f]
            for line in lines:
                hists[line[0]] = hists.get(line[0], {})
                hists[line[0]] = ast.literal_eval(line[1])
            
    else:
        hists = build_all_histograms('corel1000')
    print(rank_images(histogram, hists))

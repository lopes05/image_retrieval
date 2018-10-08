import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import ast
import os
import operator
import logging

logging.basicConfig(filename='backend.log', level=logging.DEBUG)
logger = logging.getLogger('backend')


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
    with open('http://localhost:8000/histograms.txt', 'a') as f:
        for i in histogramas.keys():
            w = str(i) + '#' + str(histogramas[i]) + '\n'
            f.write(w)
        f.close()


def build_all_histograms(path):
    histogramas = {}
    cont = 1
    print('Init histograms')
    try:
        for fil in os.listdir(path):
            print(fil)
            img = to_grayscale(cv2.imread(f'{path}/{fil}'))
            hist = calc_histograma(img)
            histogramas[fil] = hist
            cont += 1
    except Exception as e:
        logger.info(path)
        logger.error(str(type(e)))

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
    euc_diff_sorted = []
    try:
        for f in files:
            euclidian_diff[f] = euclidian_diff.get(f, 0)
            norm_img_hist = normalize_hist(img_hist)
            norm_histograms = normalize_hist(histograms[f])
            for pix_value in norm_img_hist:
                pix_distance = euclidian_distance(norm_img_hist[pix_value], norm_histograms[pix_value])
                euclidian_diff[f] += pix_distance
            euclidian_diff[f] = math.sqrt(euclidian_diff[f])
            euc_diff_sorted = sorted(euclidian_diff.items(), key=operator.itemgetter(1))
    except Exception as e:
        logger.error(str((e, type(e), f)))


    return euc_diff_sorted

import requests

def run_process(imgurl):
    img = cv2.imread(imgurl)
    aux = to_grayscale(img)
    
    histogram = calc_histograma(aux)
    #if os.path.exists('http://localhost:8000/histograms.txt'):
    req = requests.get('http://localhost:8000/histograms.txt')
    if req.status_code == 200:
        hists = {}
        try:
            f = str(req.content)
            lines = [line.split('#') for line in f.split('\\n')]
            for line in lines:
                try:
                    if line[0] and line[0] != "'":
                        hists[line[0]] = hists.get(line[0], {})
                        hists[line[0]] = ast.literal_eval(line[1])
                except:
                    print(line[0])
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())        
    else:
        hists = build_all_histograms('/home/gustavo/GustavoUNB/tcc/corel1000')
    return rank_images(histogram, hists)

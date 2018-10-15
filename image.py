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


query_hist = {}

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
    with open('./histograms.txt', 'a') as f:
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

def normalize_hist(hist, ok=True):
    hist_norm = {}
    total = np.sum(list(hist.values()))
    for pix in hist:
        hist_norm[pix] = hist_norm.get(pix, hist[pix])
        hist_norm[pix] /= total
    if not ok:
        logger.info(hist)
        logger.info(hist_norm)

    return hist_norm

def euclidian_distance(v1, v2):
    return (v1 - v2)**2

def manhatan_distance(v1, v2):
    return abs(v1 - v2)

def rank_images(img_hist, histograms, ok=True):
    files = list(histograms.keys())
    euclidian_diff = {}
    euc_diff_sorted = []
    
    try:
        norm_img_hist = normalize_hist(img_hist, ok=ok)
        for f in files:
            euclidian_diff[f] = euclidian_diff.get(f, 0)
            norm_histograms = normalize_hist(histograms[f])
            for pix_value in norm_img_hist:
                pix_distance = euclidian_distance(norm_img_hist[pix_value],\
                                                  norm_histograms[pix_value])
                #pix_distance = manhatan_distance(norm_img_hist[pix_value], norm_histograms[pix_value])
                euclidian_diff[f] += pix_distance
            euclidian_diff[f] = math.sqrt(euclidian_diff[f])
            euc_diff_sorted = sorted(euclidian_diff.items(), key=operator.itemgetter(1))
    except Exception as e:
        logger.error(str((e, type(e), f)))

    
    dx = {}
    for el in euc_diff_sorted:
        dx[el[0]] = el[1]
    
    return dx

import requests

def get_hists():
    hists = {}
    with open('./histograms.txt', 'r') as f:
        lines = [line.split('#') for line in f]
        for line in lines:
            hists[line[0]] = hists.get(line[0], {})
            hists[line[0]] = ast.literal_eval(line[1])
    return hists

def run_process(imgurl):
    global query_hist
    img = cv2.imread(imgurl)
    aux = to_grayscale(img)
    logger.info('o')
    histogram = calc_histograma(aux)
    logger.info('oi')
    query_hist = histogram.copy()
    if os.path.exists('./histograms.txt'):
        hists = {}
        try:
            hists = get_hists()
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())        
    else:
        hists = build_all_histograms('../corel1000')
    return rank_images(histogram, hists)

def refilter_imgs(data):
    global query_hist
    hists = get_hists() # todos histogramas
    useful_data = [x for x in data if x['relevant']] # apenas os marcados como relevantes
    irrelevant = [x for x in data if not x['relevant']]
    original_hist = query_hist
    logger.info(len(useful_data))
    histogramas = [list(hists[x['img']].values()) for x in useful_data]
    new_sum = np.sum(histogramas, axis=0) # soma da qtde de cada tom de cinza
    new_sum = new_sum // len(useful_data)

    irr = [list(hists[x['img']].values()) for x in irrelevant]
    irr_sum = np.sum(irr, axis=0) # soma da qtde de cada tom de cinza
    irr_sum = irr_sum // len(irrelevant)

    new_hist = list(original_hist.values()) + np.absolute(np.subtract(new_sum, 0))
    
    dic = {x:new_hist[x] for x in range(0,256)}
    query_hist = dic

    logger.info(query_hist)
    return rank_images(dic, hists) # normaliza o histograma e compara com os da base
    
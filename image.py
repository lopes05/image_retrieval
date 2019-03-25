import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import ast
import os
import operator
import logging
import math
import requests


logging.basicConfig(filename='backend.log', level=logging.DEBUG)
logger = logging.getLogger('backend')

query_hist = {}

class ImageProperties():

    def to_grayscale(img):
        """
            Returns an array of dimension Width X Height
            p[i] = (R[i] + G[i] + B[i]) // 3
        """
        img = [[sum(pixel) // 3 for pixel in line] for line in img]
        img = np.array(img)
        return img

    def calc_histograma(img):
        """
            Returns an dict {0: x, ..., n: y} of 256
        """
        imgflat = img.flatten()
        dic = {x:0 for x in range(0,256)}
        for pixel in imgflat:
            dic[pixel] += 1
        
        return dic


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


class ProjectServices():

    def save_histograms(histogramas):
        with open('./histograms.txt', 'a') as f:
            for i in histogramas.keys():
                w = str(i) + '#' + str(histogramas[i]) + '\n'
                f.write(w)
            f.close()


    def build_all_histograms(path):
        histogramas = {}
        cont = 1
        logger.info('Init histograms')
        try:
            for fil in os.listdir(path):
                logger.info(fil)
                img = to_grayscale(cv2.imread(f'{path}/{fil}'))
                #img = cv2.cvtColor(cv2.imread(f'{path}/{fil}'), cv2.COLOR_RGB2GRAY)
                hist = calc_histograma(img)
                histogramas[fil] = hist
                cont += 1
        except Exception as e:
            logger.info(path)
            logger.error(str(type(e)))

        save_histograms(histogramas)
        logger.info('Histograms saved!')
        return histogramas

    def get_hists(path='./histograms.txt'):
        hists = {}
        with open(path, 'r') as f:
            lines = [line.split('#') for line in f]
            for line in lines:
                hists[line[0]] = hists.get(line[0], {})
                hists[line[0]] = ast.literal_eval(line[1])
        return hists



class CBIR():

    def __init__(self):
        self.query_hist = None

    @staticmethod
    def euclidian_distance(v1, v2):
        return (v1 - v2)**2

    @staticmethod
    def manhatan_distance(v1, v2):
        return abs(v1 - v2)

    def rank_images(self, img_hist, histograms, ok=True):
        files = list(histograms.keys())
        euclidian_diff = {}
        euc_diff_sorted = []
        
        try:
            norm_img_hist = ImageProperties.normalize_hist(img_hist, ok=ok)
            for f in files:
                euclidian_diff[f] = euclidian_diff.get(f, 0)
                norm_histograms = ImageProperties.normalize_hist(histograms[f])
                for pix_value in norm_img_hist:
                    #pix_distance = euclidian_distance(norm_img_hist[pix_value],\
                    #                                 norm_histograms[pix_value])
                    pix_distance = CBIR.manhatan_distance(norm_img_hist[pix_value], norm_histograms[pix_value])
                    euclidian_diff[f] += pix_distance
                #euclidian_diff[f] = math.sqrt(euclidian_diff[f])
                euc_diff_sorted = sorted(euclidian_diff.items(), key=operator.itemgetter(1))[:20]
        except Exception as e:
            logger.error(str((e, type(e), f)))

        
        dx = {}
        for el in euc_diff_sorted:
            dx[el[0]] = el[1]
        logger.info(dx)
        return dx

    def run_process(self, imgurl):
        global query_hist
        img = cv2.imread(imgurl)
        aux = ImageProperties.to_grayscale(img)
        #aux = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        logger.info('o')
        histogram = ImageProperties.calc_histograma(aux)
        logger.info('oi')
        self.query_hist = histogram.copy()
        if os.path.exists('histograms.txt'):
            hists = {}
            try:
                hists = ProjectServices.get_hists()
            except Exception as e:
                import traceback
                logger.error(traceback.format_exc())        
        else:
            logger.info('rebuild')
            hists = ProjectServices.build_all_histograms('../corel1000')
        return self.rank_images(histogram, hists)

    def refilter_imgs(self, data):
        #global query_hist
        hists = ProjectServices.get_hists() # todos histogramas
        
        useful_data = [x for x in data if x['relevant']] # apenas os marcados como relevantes
        irrelevant = [x for x in data if x['irrelevant']]
        tantofaz = [x for x in data if x not in useful_data and x not in irrelevant]

        original_hist = self.query_hist

        tamrel = 1
        if useful_data:
            histogramas = [list(hists[x['img']].values()) for x in useful_data]
            tamrel = len(useful_data)
        else:
            histogramas = [[0] * 256]

        rel_sum = np.sum(histogramas, axis=0) # soma da qtde de cada tom de cinza
        rel_sum = rel_sum // tamrel

        tamirrel = 1
        if irrelevant:
            irr = [list(hists[x['img']].values()) for x in irrelevant]
            tamirrel = len(irrelevant)
        else:
            irr = [[0] * 256]

        irr_sum = np.sum(irr, axis=0) # soma da qtde de cada tom de cinza
        irr_sum = irr_sum // tamirrel

        logger.info('------------')
        logger.info(rel_sum)
        logger.info(irr_sum)
        logger.info('-----------')

        new_hist = list(original_hist.values()) + np.subtract(rel_sum, irr_sum)
        
        dic = {x:new_hist[x] for x in range(0,256)}
        self.query_hist = dic
        logger.info(self.query_hist)
        return self.rank_images(dic, hists) # normaliza o histograma e compara com os da base
        


class RelevanceFeedbackProjection():
    def __init__(self, hist_query, relevants, irrelevants):
        self.query = hist_query
        self.irrelevants = irrelevants
        self.relevants = relevants
        self.rel_len = len(self.relevants)
        self.irr_len = len(self.irrelevants)

    
    def minRI_maxRI(self):
        minRI = [10000000] * 256
        maxRI = [0] * 256
        for vetor in (relevants + irrelevants):
            for i in range(len(vetor)):
                minRI[i] = min(minRI[i], vetor[i])
                maxRI[i] = max(maxRI[i], vetor[i])

        return minRI, maxRI

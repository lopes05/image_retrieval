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

    @staticmethod
    def save_histograms(histogramas):
        with open('./histograms.txt', 'a') as f:
            for i in histogramas.keys():
                w = str(i) + '#' + str(histogramas[i]) + '\n'
                f.write(w)
            f.close()

    @staticmethod
    def build_all_histograms(path):
        histogramas = {}
        cont = 1
        logger.info('Init histograms')
        try:
            for fil in os.listdir(path):
                logger.info(fil)
                img = ImageProperties.to_grayscale(cv2.imread(f'{path}/{fil}'))
                #img = cv2.cvtColor(cv2.imread(f'{path}/{fil}'), cv2.COLOR_RGB2GRAY)
                hist = ImageProperties.calc_histograma(img)
                hist = ImageProperties.normalize_hist(hist)
                histogramas[fil] = hist
                cont += 1
        except Exception as e:
            logger.info(path)
            logger.error(str(type(e)))

        ProjectServices.save_histograms(histogramas)
        logger.info('Histograms saved!')
        return histogramas

    @staticmethod
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
        self.normalized_query = None

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
            norm_img_hist = img_hist
            for f in files:
                euclidian_diff[f] = euclidian_diff.get(f, 0)
                norm_histograms = histograms[f]
                for pix_value in norm_img_hist:
                    #pix_distance = euclidian_distance(norm_img_hist[pix_value],\
                    #                                 norm_histograms[pix_value])
                    pix_distance = CBIR.manhatan_distance(norm_img_hist[pix_value], norm_histograms[pix_value])
                    euclidian_diff[f] += pix_distance
                #euclidian_diff[f] = math.sqrt(euclidian_diff[f])
                euc_diff_sorted = sorted(euclidian_diff.items(), key=operator.itemgetter(1))[:10]
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

        logger.info(type(histogram))
        self.normalized_query = ImageProperties.normalize_hist(self.query_hist)
        self.query_hist = self.normalized_query.copy()
        
        return self.rank_images(self.query_hist, hists)

    def refilter_imgs(self, data):
        #global query_hist
        hists = ProjectServices.get_hists() # todos histogramas
        
        useful_data = [x for x in data if x['relevant']] # apenas os marcados como relevantes
        irrelevant = [x for x in data if x['irrelevant']]
        tantofaz = [x for x in data if x not in useful_data and x not in irrelevant]

        original_hist = self.query_hist
        
        tamrel = 1
        if len(useful_data):
            histogramas = [list(hists[x['img']].values()) for x in useful_data]
            tamrel = len(useful_data)
        else:
            histogramas = [[0] * 256]
        
        rel_sum = np.sum(histogramas, axis=0) # soma da qtde de cada tom de cinza
        rel_sum = rel_sum / tamrel

        tamirrel = 1
        if len(irrelevant):
            irr = [list(hists[x['img']].values()) for x in irrelevant]
            tamirrel = len(irrelevant)
        else:
            irr = [[0] * 256]

        irr_sum = np.sum(irr, axis=0) # soma da qtde de cada tom de cinza
        irr_sum = irr_sum / tamirrel

        logger.info('------------')
        logger.info(rel_sum)
        logger.info(irr_sum)
        logger.info('-----------')

        new_hist = list(original_hist.values()) + np.subtract(rel_sum, irr_sum)
        
        dic = {x:new_hist[x] for x in range(0,256)}
        self.query_hist = dic
        logger.info(self.query_hist)
        return self.rank_images(dic, hists) # normaliza o histograma e compara com os da base
        

    def multiple_query_point_search(self, data):
        relevant = [x for x in data if x['relevant']] # apenas os marcados como relevantes
        irrelevant = [x for x in data if x['irrelevant']]
        original_hist = list(self.normalized_query.values())
        hists = ProjectServices.get_hists()
        
        histogramas_rels = [list(hists[x['img']].values()) for x in relevant]
        histogramas_irrels = [list(hists[x['img']].values()) for x in irrelevant]
        
        logger.info("CRIANDO PHANTOM OBJECT")
        logger.info(histogramas_rels)
        rfp = RelevanceFeedbackProjection(original_hist, histogramas_rels, histogramas_irrels)
        
        phantom_object = rfp.calc_new_object()
        logger.info("PHANTOM OBJECT CRIADO")
        queries = histogramas_rels + [phantom_object]

        vetorretorno = []
        logger.info(len(queries))
        cont = 0
        for imagehist in queries:
            hist_tmp = {x:imagehist[x] for x in range(0,256)}
            results = self.rank_images(hist_tmp, hists)
            vetorretorno.append(results)
            logger.info("done query " + str(cont))
            cont += 1

        logger.info(vetorretorno)
        logger.info("OK. done multiple queries")
        # combinar resultados
        
        """
        conjunto = {}
        for retorno in vetorretorno:
            for localhist in retorno:
                conjunto[localhist] = retorno[localhist]

        logger.info(conjunto)
        logger.info(len(conjunto))
        conjunto = sorted(conjunto.items(), key=operator.itemgetter(1))[:10]
        logger.info(conjunto)
        listaconjunto = list(conjunto)
        dx = {}
        for el in conjunto:
            dx[el[0]] = el[1]
        logger.info(dx)
        return dx
        """
        teste = self.distancia_combinada(vetorretorno, hists)
        return vetorretorno[0]

    def calc_single_dist(self, a, b):
        #dists = []
        dist = 0
        logger.info(a)
        logger.info(b)
        for pix in a:
            dist += CBIR.manhatan_distance(a[pix], b[pix])

        return dist

    def distancia_combinada(self, listageral, hists):
        dists_originais = {}
        
        for lista in listageral:
            for elemento in lista:
                logger.info(elemento)
                dist_original = self.calc_single_dist(self.normalized_query, hists[elemento])
                dists_originais[elemento] = dist_original
        somaoriginais = 0
        logger.info("xuxu")
        for chave in dists_originais:
            somaoriginais += dists_originais[chave]
        
        dlinhas = []
        for lista in listageral:
            for elemento in lista:
                pesoi = 1
                pesototal = 1*len(lista)
                dlinha = ((lista[elemento] * pesoi) / pesototal) + (lista[elemento] * somaoriginais / dists_originais[elemento]) 
                dlinhas.append((dlinha, elemento))
        #novadistancral:
            
        logger.info(dlinhas)
        return dlinhas
    

class RelevanceFeedbackProjection():
    def __init__(self, hist_query, relevants, irrelevants):
        self.query = hist_query
        self.irrelevants = irrelevants
        self.relevants = relevants
        self.rel_len = len(self.relevants)
        self.irr_len = len(self.irrelevants)
        self.minRI, self.maxRI = self.calc_minRI_maxRI()
        self.minSI, self.maxSI = self.calc_minSI_maxSI()
        self.delta = np.subtract(self.maxRI, self.minRI)
        self.p1, self.p2 = self.calc_pontos_projecao()
        self.t1, self.t2 = self.calc_tam_retas()
        self.projp1, self.projp2 = self.calc_projecoes()
        self.vet_dists, self.sum_dists = self.calc_dist_rels()
        self.vet_weight = [1] * self.rel_len
        self.sumweights = np.sum(self.vet_weight) 
        self.avg = self.calc_avg()
    
    def calc_minRI_maxRI(self):
        minRI = [10000000] * len(self.query)
        maxRI = [0] * len(self.query)
        for vetor in (self.relevants):
            for i in range(len(vetor)):
                minRI[i] = min(minRI[i], vetor[i])
                maxRI[i] = max(maxRI[i], vetor[i])

        return minRI, maxRI

    def calc_minSI_maxSI(self):
        minSI = [10000000] * len(self.query)
        maxSI = [0] * len(self.query)
        for vetor in (self.irrelevants):
            for i in range(len(vetor)):
                minSI[i] = min(minSI[i], vetor[i])
                maxSI[i] = max(maxSI[i], vetor[i])

        return minSI, maxSI

    def calc_pontos_projecao(self):
        p1, p2 = [0] * len(self.query), [0] * len(self.query)
        for i in range(len(self.delta)):
            p1 = self.minRI[i] - self.delta[i]
            p2 = self.maxRI[i] + self.delta[i]

        return p1, p2

    def calc_tam_retas(self):
        t1, t2 = [0] * len(self.query), [0] * len(self.query)
        for i in range(len(self.minSI)):
            t1[i] = abs(self.minSI[i] - self.p1)
            t2[i] = abs(self.p2 - self.maxSI[i])
        return t1, t2

    def calc_projecoes(self):
        projp1 = [0] * len(self.query)
        projp2 = [0] * len(self.query)
        
        for i in range(len(self.minRI)):
            projp1[i] = self.minRI[i] + self.t1[i]
            projp2[i] = self.maxRI[i] - self.t2[i]
            
            if self.minSI[i] >= self.minRI[i]:
                projp1[i] = self.minRI[i]
            if self.maxSI[i] <= self.maxRI[i]:
                projp2[i] = self.maxRI[i]

        return projp1, projp2

    def calc_dist_rels(self):
        dists = []
        for img in self.relevants:
            dist = 0
            for indice in range(len(img)):
                dist += abs(self.query[indice] - img[indice])
            dists.append(dist)
        return dists, np.sum(dists)

    def calc_weight_relevants(self):
        pass

    def calc_avg(self):
        avg = []

        for featureindex in range(len(self.query)):
            soma = 0
            for imageindex in range(len(self.relevants)):
                #self.sum_dists = 0.0000 + 0.0038 + 0.0137
                #self.vet_dists = [0.0000, 0.0038, 0.0137]
                # e se a divisao for por 0
                dists_calc = self.vet_dists[imageindex] / self.sum_dists
            
                weights_calc = self.vet_weight[imageindex] / self.sumweights
                print(dists_calc, weights_calc)

                feature = self.relevants[imageindex][featureindex]
                print('feature', feature)
                conta = ((feature * dists_calc + feature * weights_calc))
                print('conta>', conta)
                soma += conta
            avg.append(soma/2)
        logger.info("eu?")
        return avg

    def calc_new_object(self):
        new_obj = [0] * len(self.query)
        for i in range(len(new_obj)):
            new_obj[i] = (self.projp1[i] + self.projp2[i] + self.avg[i]) / 3
        
        return new_obj
from image import *
import os

def calc_precision_single_query(resultados, classname):
    p = 0
    for chave in resultados:
        if classname in chave:
            p += 1
    precision = p / len(resultados)
    return precision

import json

def mock_json(resultados, classname, tecnica):
    jsonn = []
    for arq in resultados:
        if classname in arq:
            jsonn.append({'img': arq, 'relevant': True, 'irrelevant': False })
        else:
            jsonn.append({'img': arq, 'relevant': False, 'irrelevant': True })

    jsonn.append({'classname': classname}) 
    jsonn.append({'tecnica': tecnica})
        

    return jsonn

def collect_cbir(tecnica):
    cont = 0
    avg_geral = []
    print(f"START {tecnica}")
    avg_classes = {'Hors':[], 'Food':[], 'Dino':[], 'Moun':[], 'Elep':[], 'Afri':[], 'Beac':[], 'Buse':[], 'Buil':[], 'Flow':[]}
    with open('single_results.txt', 'a') as arquivo:
        for fil in os.listdir('corel1000'):
            print(f"ARQUIVO {fil}")
            avg_file = []
            
            cbir = CBIR()
            hists = cbir.run_process(f'corel1000/{fil}')
            avg_file.append(calc_precision_single_query(hists, fil[:4]))
            
            for i in range(4):
                jsonn = mock_json(hists, fil[:4], tecnica)
                tecnica = jsonn.pop()['tecnica']
                nomeclasse = jsonn.pop()['classname']
                if tecnica == "qpm":
                    hists = cbir.refilter_imgs(jsonn)
                elif tecnica == "multiquery":
                    hists = cbir.multiple_query_point_search(jsonn)
                elif tecnica == "rfra":
                    hists = cbir.rfra(jsonn)
                avg_file.append(calc_precision_single_query(hists, fil[:4]))

            print(avg_file)
            arquivo.write(fil + ':' + str(avg_file) + '\n')
            avg_geral.append((fil, np.mean(avg_file)))
            cont += 1

    for tup in avg_geral:
        fil = tup[0][:4]
        avg_classes[fil].append(tup[1])

    with open('results.txt', 'a') as f:
        f.write(tecnica + "\n")
        for classe in avg_classes:
            avg_classes[classe] = np.mean(avg_classes[classe])
            f.write(classe + ':' + str(avg_classes[classe])+'\n')
        f.write("\n")
    

        
    print(avg_geral)
    print(avg_classes)


#collect_cbir("qpm")
#collect_cbir("multiquery")
collect_cbir("rfra")
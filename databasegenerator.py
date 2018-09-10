def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        dic = pickle.load(fo, encoding='bytes')
    return dic

dic = unpickle('cifar/data_batch_1')

RED = 0
GREEN = 1
BLUE = 2

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2

matrix = []

print(dic.keys())
i = 0
for img in dic[b'data']:
    print(dic[b'filenames'][i])
    r = img[:1024]
    g = img[1024:2048]
    b = img[2048:]
    mat = list(zip(r, g, b)) # 1024 pixels
    mat = np.array(mat).reshape((32, 32, 3))
    print(mat.max(), mat.min())
    print(mat.shape)
    imagem = mat
    #cv2.imshow('im', imagem)
    #cv2.waitKey(0)
    path = f"{dic[b'filenames'][i]}"
    path.replace("'", '')
    path = path[2:-1]
    path = 'imgdatabase/' + path
    print(path)
    cv2.imwrite(path, imagem)
    i += 1

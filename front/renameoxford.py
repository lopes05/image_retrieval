import os
import numpy as np

classes = ['Daffodil','Snowdrop', 'LilyValley', 'Bluebell', 'Crocus', 'Iris', 'Tigerlily', 'Tulip', 'Fritillary', 'Sunflower', 'Daisy', 'ColtsFoot',  'Dandelalion', 'Cowslip', 'Buttercup', 'Windflower','Pansy']    
index = 0

y = np.repeat(classes, 80)

cont = 1
for file in sorted(list(os.listdir('../oxfordflowers'))):
    os.rename(f'../oxfordflowers/{file}', f'../oxfordflowers/{y[index]}{cont}.jpg')
    index += 1
    cont += 1
    cont %= 81
    if cont == 0:
        cont == 1
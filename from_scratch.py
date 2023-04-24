import shutil
import os

def clean():
    for file in os.listdir(os.getcwd()):
        if not os.path.isfile(file) and file not in ['utilities', 'src', '.git']:
            shutil.rmtree(file)

if __name__ == '__main__':
    if input('ATTENTION TOUS LES RESULTATS SERONT EFFACES !!!')=='y':clean()
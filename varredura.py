import os
import chardet

caminho = './datasets'

for nome in os.listdir(caminho):
    # Verifica se o caminho completo é um arquivo
    if os.path.isfile(os.path.join(caminho, nome)):
        with open(caminho, 'rb') as f:
            resultado = chardet.detect(f.read(10000)) # Lê os primeiros 10k bytes
            print(f'ENCODING USADO: {resultado["encoding"]}')
        print(type(nome))
        print(nome)
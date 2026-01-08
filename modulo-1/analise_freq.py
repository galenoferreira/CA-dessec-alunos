import argparse
import json
import re
from collections import Counter
from pathlib import Path
from unidecode import unidecode
import PyPDF2

def extrair_texto(arquivo: Path) -> str:
    if arquivo.suffix.lower() == '.txt':
        return arquivo.read_text(encoding='utf-8', errors='ignore')

    elif arquivo.suffix.lower() == '.json':
        with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            return json.dumps(data)

    elif arquivo.suffix.lower() == '.pdf':
        texto = ''
        with open(arquivo, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                texto += page.extract_text() or ''
        return texto

    else:
        raise ValueError(f"Tipo de arquivo não suportado: {arquivo.suffix}")

def contar_letras(texto: str) -> Counter:
    texto = unidecode(texto)  # remove acentos
    letras = re.findall(r'[a-zA-Z]', texto)
    letras = [letra.lower() for letra in letras]
    return Counter(letras)

def exibir_sumario(contador: Counter):
    total = sum(contador.values())
    print(f"\n{'Letra':<6}{'Ocorrências':>12}{'Percentual':>12}")
    print("-" * 30)
    for letra, quantidade in contador.most_common():
        percentual = (quantidade / total) * 100
        print(f"{letra.upper():<6}{quantidade:>12,}{percentual:>11.2f}%")
    print("-" * 30)
    print(f"{'Total':<6}{total:>12,}{'100.00%':>12}")

def main():
    parser = argparse.ArgumentParser(description='Analisador de frequência de letras (A-Z) em arquivos .txt, .json, .pdf')
    parser.add_argument('-f', '--file', required=True, help='Caminho do arquivo a ser analisado')
    args = parser.parse_args()

    arquivo = Path(args.file)
    if not arquivo.exists():
        print("❌ Arquivo não encontrado.")
        return

    try:
        texto = extrair_texto(arquivo)
        contador = contar_letras(texto)
        exibir_sumario(contador)
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo: {e}")

if __name__ == '__main__':
    main()


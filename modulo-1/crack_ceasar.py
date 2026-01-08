import argparse
from pathlib import Path
import re
from unidecode import unidecode

def carregar_dicionario(caminho='dicionario.txt'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return set(p.strip().lower() for p in f if p.strip())
    except FileNotFoundError:
        print("❌ Arquivo 'dicionario.txt' não encontrado.")
        exit(1)

def cifra_cesar(texto, chave):
    resultado = []
    for c in texto:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            novo = (ord(c) - base - chave) % 26 + base
            resultado.append(chr(novo))
        else:
            resultado.append(c)
    return ''.join(resultado)

def contar_palavras_validas(texto, dicionario):
    palavras = re.findall(r'\b\w+\b', unidecode(texto.lower()))
    return sum(1 for p in palavras if p in dicionario)

def gerar_nome_saida(nome_arquivo: str) -> str:
    if 'cifrado' in nome_arquivo:
        return nome_arquivo.replace('cifrado', 'decifrado')
    else:
        return nome_arquivo.rsplit('.', 1)[0] + '_decifrado.txt'

def main():
    parser = argparse.ArgumentParser(description='Decifra um texto cifrado com Cifra de César por força bruta e dicionário.')
    parser.add_argument('-f', '--file', required=True, help='Caminho do arquivo cifrado')
    args = parser.parse_args()

    arquivo = Path(args.file)
    if not arquivo.exists():
        print("❌ Arquivo não encontrado.")
        return

    try:
        try:
            texto_cifrado = arquivo.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            texto_cifrado = arquivo.read_text(encoding='latin-1')

        dicionario = carregar_dicionario()
        melhor_chave = None
        melhor_score = -1
        melhor_texto = ""

        print("🔍 Iniciando análise de chaves de 1 a 23...\n")
        for chave in range(1, 24):
            print(f"Testando chave {chave}/23...", end='\r')
            texto_decifrado = cifra_cesar(texto_cifrado, chave)
            score = contar_palavras_validas(texto_decifrado, dicionario)
            if score > melhor_score:
                melhor_score = score
                melhor_chave = chave
                melhor_texto = texto_decifrado

        print(f"\n✅ Melhor chave encontrada: {melhor_chave} ({melhor_score} palavras reconhecidas)\n")
        print("=== Início do texto decifrado ===\n")
        print(melhor_texto[:2000])  # Mostra os primeiros 2000 caracteres

        # Salva o resultado
        nome_saida = gerar_nome_saida(arquivo.name)
        caminho_saida = arquivo.parent / nome_saida
        caminho_saida.write_text(melhor_texto, encoding='utf-8')
        print(f"\n💾 Texto completo decifrado salvo em: {caminho_saida}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()


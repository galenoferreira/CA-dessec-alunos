import os

def decifra_vigenere(texto, chave):
    resultado = []
    chave = ''.join(filter(str.isalpha, chave)).lower()
    if not chave:
        raise ValueError("Chave deve conter pelo menos uma letra.")

    indice_chave = 0
    tamanho_chave = len(chave)

    for caractere in texto:
        if caractere.isalpha():
            base = ord('A') if caractere.isupper() else ord('a')
            deslocamento = ord(chave[indice_chave % tamanho_chave].lower()) - ord('a')
            novo_caractere = chr((ord(caractere) - base - deslocamento) % 26 + base)
            resultado.append(novo_caractere)
            indice_chave += 1
        else:
            resultado.append(caractere)
    return ''.join(resultado)


def main():
    try:
        arquivo = input("Digite o caminho do arquivo a ser decifrado: ").strip()
        if not os.path.isfile(arquivo):
            print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
            return

        chave = input("Digite a chave de cifra (apenas letras): ").strip()
        chave = chave.replace(" ", "")
        if not chave.isalpha() or not chave:
            print("A chave deve conter apenas letras, sem espaços.")
            return

        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            with open(arquivo, 'r', encoding='latin-1') as f:
                conteudo = f.read()

        texto_decifrado = decifra_vigenere(conteudo, chave)
        novo_arquivo = arquivo.rsplit('.', 1)[0] + '_decifrado.txt'
        with open(novo_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_decifrado)

        print(f"✅ Texto cifrado com sucesso! Arquivo salvo como: {novo_arquivo}")

    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()

import os

def cifra_cesar(texto, chave):
    # Função que aplica a cifra de César em um texto com base na chave fornecida.
    resultado = ""
    for caractere in texto:
        # Verifica se o caractere é uma letra do alfabeto.
        if caractere.isalpha():
            # Define a base ASCII dependendo se é maiúsculo ou minúsculo.
            base = ord('A') if caractere.isupper() else ord('a')
            # Aplica a cifra de César
            deslocado = (ord(caractere) - base + chave) % 26 + base
            resultado += chr(deslocado)
        else:
            # Mantém o caractere inalterado caso não seja uma letra.
            resultado += caractere
    return resultado

def main():
    try:
        # Solicita ao usuário o caminho do arquivo a ser cifrado.
        arquivo = input("Digite o caminho do arquivo a ser cifrado: ").strip()
        if not os.path.isfile(arquivo):
            print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
            return

        try:
            chave = int(input("Digite o valor de transposição (número inteiro): "))
        except ValueError:
            print("Por favor, insira um valor numérico válido.")
            return

        # Tenta abrir o arquivo com codificação UTF-8, e se falhar, tenta Latin-1
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            with open(arquivo, 'r', encoding='latin-1') as f:
                conteudo = f.read()

        texto_cifrado = cifra_cesar(conteudo, chave)

        novo_arquivo = arquivo.rsplit('.', 1)[0] + '_cifrado.txt'
        with open(novo_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_cifrado)

        print(f"✅ Texto cifrado com sucesso! Arquivo salvo como: {novo_arquivo}")

    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()


import os

def cifra_vigenere(texto, chave):
    """
    Applies the Vigenère cipher to the given text using the provided key (chave).
    The Vigenère cipher is a method of encrypting alphabetic text by using a
    series of Caesar ciphers based on the letters of a keyword. Non-alphabetic
    characters in the input text are left unchanged.

    :param texto: The input text to be encrypted. This can include alphabetic and
        non-alphabetic characters.
    :type texto: str
    :param chave: The keyword used for encryption. Only alphabetical characters
        are considered; others are ignored. It must contain at least one alphabetic
        character.
    :type chave: str
    :raises ValueError: If the provided key (chave) contains no alphabetic characters.
    :return: The resulting encrypted text after applying the Vigenère cipher. The
        alphabetic characters are shifted according to the key, while non-alphabetic
        characters remain unchanged.
    :rtype: str
    """
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
            novo_caractere = chr((ord(caractere) - base + deslocamento) % 26 + base)
            resultado.append(novo_caractere)
            indice_chave += 1
        else:
            resultado.append(caractere)
    return ''.join(resultado)


def main():
    """
    Encrypts the content of a specified file using the Vigenère cipher algorithm
    and saves the encrypted content into a new file. Prompts the user for the file
    path and a cipher key of exactly 6 alphabetic characters.

    The function reads the file as UTF-8 by default, but falls back to Latin-1
    encoding if a Unicode Decode Error occurs. The output file is named based on
    the input file, with '_vigenere.txt' appended before the file extension.

    :param arquivo: Path to the file to be encrypted, provided by user input.
    :type arquivo: str
    :param chave: Encryption key, a string of exactly six alphabetic characters.
    :type chave: str

    :raises FileNotFoundError: If the specified file does not exist.
    :raises ValueError: If the encryption key is not exactly 6 letters.
    :raises UnicodeDecodeError: If the character encoding of the file content cannot
        be processed with either UTF-8 or Latin-1.
    :raises IOError: If an error occurs when opening, reading, or writing files.
    :raises Exception: Wraps any other unexpected errors.

    :return: None
    """
    try:
        arquivo = input("Digite o caminho do arquivo a ser cifrado: ").strip()
        if not os.path.isfile(arquivo):
            print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
            return

        chave = input("Digite a chave de cifra (apenas letras, exatamente 6 caracteres): ").strip().upper()
        if len(chave) != 6 or not chave.isalpha():
            print("A chave deve conter exatamente 6 letras, sem espaços.")
            return

        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            with open(arquivo, 'r', encoding='latin-1') as f:
                conteudo = f.read()

        texto_cifrado = cifra_vigenere(conteudo, chave)
        novo_arquivo = arquivo.rsplit('.', 1)[0] + '_vigenere.txt'
        with open(novo_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_cifrado)

        print(f"✅ Texto cifrado com sucesso! Arquivo salvo como: {novo_arquivo}")

    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()

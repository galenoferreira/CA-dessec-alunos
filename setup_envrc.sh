#!/bin/bash
# ========================================================================
# Script Name   : conda_direnv_setup.sh
# Version       : 0.98
# Author        : Galeno Garbe
# Empresa       : Geonex Solutions
# E-mail        : galeno@geonex.com.br
# Description   : Cria ambiente Conda com integração ao direnv, GitHub e SSH.
#                 Suporte aos parâmetros:
#                   --create: Cria o ambiente e arquivos.
#                   --deploy: Copia os arquivos para subdiretórios imediatos.
#                   --update    Add missing environment variables (e.g., database) to .envrc without recreating the Conda environment.
# ========================================================================

# Função para mostrar o help
mostrar_ajuda() {
  echo "Uso: $0 [--create | --deploy]"
  echo ""
  echo "  --create    Cria o ambiente Conda, integra com direnv e configura GitHub."
  echo "  --deploy    Copia este script e o arquivo giti.sh para todos os subdiretórios imediatos."
  echo "  --update    Add missing environment variables (e.g., database) to .envrc without recreating the Conda environment."
  echo "  --help      Exibe esta mensagem de ajuda."
}

# Verifica se foi passado algum argumento
if [[ $# -eq 0 ]]; then
  mostrar_ajuda
  exit 0
fi

# Caminho do script atual
SCRIPT_ATUAL="$(realpath "$0")"

# Processa os argumentos
case "$1" in
  --create)
    # Verifica se o comando 'conda' está disponível
    if ! command -v conda &> /dev/null; then
      echo "Erro: o comando 'conda' não foi encontrado. Certifique-se de que o Conda está instalado e no PATH."
      exit 1
    fi

    echo "Digite o nome do ambiente Conda que deseja criar e ativar:"
    read -r CONDA_ENV

    echo "Escolha o locale desejado:"
    echo "[B] pt_BR (padrão)"
    echo "[U] en_US"
    read -r LOCALE_CHOICE

    # Prompt for database root password
    read -s -p "Enter database root password: " ROOT_DB_PASS; echo
    # Prompt for new database user password
    read -s -p "Enter password for DB user $CONDA_ENV: " DB_PASS; echo

    if [[ "$LOCALE_CHOICE" =~ ^[Uu]$ ]]; then
      LC_SETTING='en_US.UTF-8'
    else
      LC_SETTING='pt_BR.UTF-8'
    fi

    # Verifica se foi informado o nome
    if [[ -z "$CONDA_ENV" ]]; then
      echo "Nenhum ambiente informado. Abortando."
      exit 1
    fi

    # Cria o ambiente Conda com Python 3.12
    conda create --name "$CONDA_ENV" python=3.12 -y

    # Cria o arquivo .envrc com comandos para ativar o Conda automaticamente via direnv
    cat <<EOF > .envrc
#!/bin/bash
# Carrega o script de configuração do Conda
source "\$(conda info --base)/etc/profile.d/conda.sh"

# Environment
export STAGE=DEV

# Ativa o ambiente
conda activate $CONDA_ENV

# Adiciona variavel com o nome do repositorio
GITHUB_REPO=$CONDA_ENV

export GITHUB_REPO
# Adiciona o diretório atual ao PATH

REP_DIR=\$(pwd)
export REP_DIR

export COMPOSE_BAKE=true
PATH="\$PATH:."
export LC_ALL="pt_BR.UTF-8"
export DB_NAME=$CONDA_ENV
export DB_USER=$CONDA_ENV
export DB_ROOT_PASSWORD="\$ROOT_DB_PASS"
export DB_PASSWORD="\$DB_PASS"

# Function to render colored stage marker in the prompt
prompt_stage() {
  case "\${STAGE}" in
    PROD)
      echo "%{\$fg_bold[white]%}%{\$bg[red]%}<<\${STAGE}>>%{\$reset_color%}"
      ;;
    DEV)
      echo "%{\$fg_bold[white]%}%{\$bg[green]%}<<\${STAGE}>>%{\$reset_color%}"
      ;;
    QA)
      echo "%{\$fg_bold[white]%}%{\$bg[yellow]%}<<\${STAGE}>>%{\$reset_color%}"
      ;;
    *)
      echo "<<\${STAGE}>>"
      ;;
  esac
}

# Prepend the colored stage marker to PS1
export PS1="\$(prompt_stage) \$PS1"

EOF

    echo "Arquivo .envrc criado com sucesso em $(pwd)"

    # Create PostgreSQL database and user
    PGPASSWORD="$ROOT_DB_PASS" psql -U postgres -h localhost -c "CREATE DATABASE \"$CONDA_ENV\";"
    PGPASSWORD="$ROOT_DB_PASS" psql -U postgres -h localhost -c "CREATE USER \"$CONDA_ENV\" WITH PASSWORD '$DB_PASS';"
    PGPASSWORD="$ROOT_DB_PASS" psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE \"$CONDA_ENV\" TO \"$CONDA_ENV\";"

    echo "Execute 'direnv allow' para autorizar o uso deste arquivo."

    # Ativa o agente SSH e adiciona a chave padrão
    eval "$(ssh-agent -s)"
    ssh-add \$SSH_DIR/github_main

    # Cria .gitignore com regras úteis
    echo "*.pem" > .gitignore
    echo "$CONDA_ENV" >> .gitignore
    echo "*.log" >> .gitignore

    # Gera chave SSH e configura repositório GitHub
    ssh-keygen -t rsa -C "$CONDA_ENV"
    gh auth login
    gh repo create "$CONDA_ENV" --private

    git init
    git add .
    git commit -m "Initial commit"
    git remote add origin "git@github.com:galenoferreira/$CONDA_ENV.git"
    git checkout -b master
    git push -u origin master

    direnv allow

    echo "📝 Gerando resumo do ambiente em env_summary.txt..."

    cat <<SUMMARY > env_summary.txt
📦 Conda Environment Setup Summary
==============================
🔹 Nome do Ambiente: $CONDA_ENV
🌐 Locale: $LC_SETTING
🛠️ Conda Python Version: 3.12
📂 Diretório: $(pwd)
📄 Arquivo .envrc criado: ✅
🔐 SSH configurado: ✅ (chave github_main adicionada)
🌍 Repositório GitHub: https://github.com/galenoferreira/$CONDA_ENV
🗃️ Git branch inicial: master

DISCLAIMER: Verifique segurança com 'git secrets --scan -r' antes de tornar qualquer repositório público!

✅ Execute 'direnv allow' caso ainda não tenha feito isso.

🧪 Teste seu ambiente com:
conda activate $CONDA_ENV
python --version
SUMMARY

    echo "Resumo salvo em env_summary.txt ✅"
    ;;

  --update)
    echo "🛠️ Updating .envrc with missing variables..."

    # Ensure .envrc exists
    if [[ ! -f .envrc ]]; then
      echo "❌ .envrc not found. Run --create first."
      exit 1
    fi

    # Add DB_NAME and DB_USER if missing
    grep -q '^export DB_NAME=' .envrc || echo "export DB_NAME=$CONDA_ENV" >> .envrc
    grep -q '^export DB_USER=' .envrc || echo "export DB_USER=$CONDA_ENV" >> .envrc

    # Prompt for root and user passwords if missing and append
    if ! grep -q '^export DB_ROOT_PASSWORD=' .envrc; then
      read -s -p "Enter database root password: " ROOT_DB_PASS; echo
      echo "export DB_ROOT_PASSWORD=\"$ROOT_DB_PASS\"" >> .envrc
    fi
    if ! grep -q '^export DB_PASSWORD=' .envrc; then
      read -s -p "Enter password for DB user $CONDA_ENV: " DB_PASS; echo
      echo "export DB_PASSWORD=\"$DB_PASS\"" >> .envrc
    fi

    echo "✅ .envrc updated."
    ;;
  
  --deploy)
    echo "Copiando arquivos para subdiretórios imediatos..."

    for pasta in */; do
      if [[ -d "$pasta" ]]; then
        cp "$SCRIPT_ATUAL" "$pasta"
        cp "giti.sh" "$pasta"
        echo "Copiado para: $pasta"
      fi
    done

    echo "Cópia concluída!"
    ;;

  --help)
    mostrar_ajuda
    ;;

  *)
    echo "Parâmetro inválido: $1"
    mostrar_ajuda
    exit 1
    ;;
esac

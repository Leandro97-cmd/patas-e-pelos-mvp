# Patas e Pelos

MVP para organizar as informações de um pequeno negócio de banho e tosa.
O fluxo planejado é **Tutor → Animal → Agendamento → Consulta da agenda**.

## Etapa atual

Etapa 2: autenticação de colaboradores, sessão, proteção das páginas internas
e logout. A etapa 1 foi registrada no commit `1997ba5`.

Não há cadastro de tutores, animais, agendamentos, histórico ou pagamentos.
Também não há cadastro público de colaboradores, recuperação de senha ou
GitHub Actions nesta etapa.

## Tecnologias

- Python 3.12.
- Flask 3.x e templates Jinja.
- Bootstrap 5.3.8, carregado por CDN com verificação de integridade.
- SQLite da biblioteca padrão do Python, somente para colaboradores.
- Argon2id com `argon2-cffi`, para armazenamento de senhas.
- Flask-WTF para proteção CSRF dos formulários.
- pytest com testes isolados de autenticação.

É necessário acesso à internet para instalar dependências e carregar o Bootstrap.
Os estilos locais mantêm a página legível se o CDN estiver indisponível.

## Instalação e execução no Windows (PowerShell)

Tenha uma instalação funcional do Python 3.12. Confirme a versão:

```powershell
python --version
```

Se o comando não funcionar ou apresentar outra versão, use o caminho completo
do executável Python 3.12. Não é necessário alterar a política de execução do
PowerShell nem ativar o ambiente virtual.

Na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Depois siga a seção **Configurar o acesso local** abaixo antes de iniciar.

### Alternativa com o Python 3.12 incluído no ambiente Codex desta máquina

Use esta alternativa somente se o executável abaixo existir:

```powershell
& "C:\Users\Leandro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Esse caminho é específico desta máquina. Para outros computadores, utilize
uma instalação própria do Python 3.12 e os comandos da seção anterior.

### Problema de permissão na pasta temporária

Durante a preparação neste ambiente, `python` apontou para um atalho do Windows
que não executava. Foi utilizado o Python 3.12.14 do caminho alternativo acima.
A preparação do pip também encontrou uma restrição de escrita na pasta
temporária do ambiente. Se ocorrer o mesmo erro após a criação de `.venv/`,
use uma pasta temporária dentro do ambiente virtual:

```powershell
New-Item -ItemType Directory -Force -Path .venv\tmp | Out-Null
$env:TEMP = (Resolve-Path -LiteralPath .venv\tmp).Path
$env:TMP = $env:TEMP
.\.venv\Scripts\python.exe -m ensurepip --upgrade --default-pip
.\.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
```

Essas variáveis valem somente para a sessão atual do terminal.

## Configurar o acesso local

### 1. Chave de sessão

Na mesma janela do PowerShell que será usada para iniciar o sistema, gere
uma chave aleatória sem exibi-la:

```powershell
$env:PATAS_SECRET_KEY = (& .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))")
```

A aplicação exige uma chave de pelo menos 32 caracteres e recusa iniciar sem
ela. O comando acima gera 64 caracteres aleatórios. Não coloque a chave no
código-fonte, README, commit, captura de tela ou mensagem pública.

Essa variável vale apenas para o terminal atual. Em uso contínuo, guarde a
mesma chave de forma privada em um gerenciador de segredos ou variável de
ambiente do serviço que inicia a aplicação. O projeto não carrega arquivos
`.env` automaticamente. Gerar outra chave invalida as sessões anteriores,
mas não apaga os colaboradores nem suas senhas armazenadas.

### 2. Banco e colaborador fictício

```powershell
.\.venv\Scripts\python.exe -m flask --app run init-db
.\.venv\Scripts\python.exe -m flask --app run create-colaborador --nome "Colaborador Demo" --usuario "demo.local"
```

O segundo comando solicita uma senha e sua confirmação, sem exibir o que é
digitado. Escolha uma senha fictícia exclusiva para esta demonstração, com
12 a 128 caracteres. Não utilize suas credenciais pessoais.

Não há senha padrão ou colaborador criado automaticamente. A senha não é
passada como argumento nem gravada em texto simples. Somente seu hash
Argon2id é persistido, com salt individual. Os dados armazenados são:
`id`, `nome`, `usuario` e `senha_hash`.

O nome deve ter de 1 a 100 caracteres. O usuário deve ter de 3 a 64 caracteres,
usando letras sem acentos, números, ponto, hífen ou sublinhado. Espaços nas
extremidades são removidos; maiúsculas e minúsculas identificam o mesmo
usuário. Não são aceitos usuários duplicados. A senha mantém exatamente os
caracteres digitados e não pode conter apenas espaços.

O banco fica em `instance/patas_e_pelos.sqlite3`, excluído do Git. O comando
`init-db` pode ser executado novamente sem apagar colaboradores existentes.
Proteja o arquivo com as permissões do sistema operacional; SQLite não está
criptografado. Caso precise de backup local, copie o banco com a aplicação
encerrada e mantenha a cópia em local privado.

### 3. Iniciar

```powershell
.\.venv\Scripts\python.exe run.py
```

Abra <http://127.0.0.1:5000>. O sistema direciona para `/login`. Entre com
`demo.local` e a senha que você definiu. Após o login, a página inicial interna
mostra o nome do colaborador e o botão **Sair**. Para encerrar o servidor,
pressione `Ctrl+C` no terminal.

## Segurança e limites desta etapa

- Rotas internas exigem sessão; somente login e arquivos estáticos são públicos.
- Credenciais são validadas no servidor. Login inválido usa sempre a mensagem
  “Usuário ou senha inválidos.”, sem identificar qual campo estava incorreto.
- Sessões são assinadas pelo Flask, com duração de até 8 horas e cookies
  `HttpOnly` e `SameSite=Lax`. A sessão contém identificador de usuário e
  metadados técnicos, sem nome, senha ou hash. Cookies assinados não são cifrados.
- A sessão anterior é limpa ao entrar. O logout exige POST com token CSRF e
  remove a sessão do navegador. As respostas dinâmicas usam `Cache-Control: no-store`.
- Login e logout têm proteção CSRF. Jinja escapa os dados exibidos, e as
  consultas SQLite usam parâmetros. Erros do banco não expõem detalhes na página.
- O servidor atual usa HTTP apenas em `127.0.0.1`, com depuração desativada.
  Por isso, o cookie `Secure` fica desativado no uso local. Antes de disponibilizar
  o sistema por HTTPS, configure `$env:PATAS_COOKIE_SECURE = "1"` no serviço.
- Esta entrega é para demonstração local. Publicação na internet ainda exige
  servidor de produção, HTTPS e limitação de tentativas de login. Não há gestão
  centralizada de sessões nem revogação imediata de cópias de cookies roubados;
  esses cookies permanecem sujeitos ao prazo de expiração e à validade da chave.

## Organização

```text
patas e pelos/
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
├── pytest.ini
├── app/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── colaboradores.py
│   │   └── database.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── error.html
│   │   ├── index.html
│   │   └── login.html
│   └── static/
│       └── css/
│           └── style.css
└── tests/
    ├── .gitkeep
    ├── conftest.py
    └── test_auth.py
```

- `run.py`: entrada para iniciar o servidor local.
- `app/__init__.py`: função `create_app(test_config=None)`, configuração e registro de rotas.
- `app/config.py`: configurações iniciais, sem credenciais.
- `app/cli.py`: comandos locais para preparar o banco e criar colaboradores.
- `app/presentation/`: rotas HTTP; templates e arquivos estáticos compõem a interface.
- `app/services/`: validação e autenticação de colaboradores com Argon2id.
- `app/repositories/`: conexão e persistência SQLite com consultas parametrizadas.
- `tests/` e `pytest.ini`: preparação para testes automatizados.
- `.gitignore`: impede versionar ambientes virtuais, caches, segredos e bancos locais.

## Testes da autenticação

Execute:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Os testes usam bancos temporários, chaves aleatórias e colaboradores fictícios.
Não é necessário definir `PATAS_SECRET_KEY`, criar um banco real ou configurar
um usuário de demonstração para executar a suíte. CSRF permanece habilitado.

A suíte verifica login válido e inválido, acesso protegido, logout, CSRF,
hashes Argon2id, validação, duplicidade, consultas parametrizadas, escape de
HTML, cookies, usuário removido, chave obrigatória e comandos locais.

## Próximo commit

Revise as alterações antes de versionar. Não adicione `.venv/`, `instance/`,
chaves, senhas ou bancos locais ao Git.

```powershell
git diff
git add README.md requirements.txt app tests/conftest.py tests/test_auth.py
git status --short
git commit -m "feat: adiciona autenticação de colaboradores"
```

O commit não é feito automaticamente. As próximas funcionalidades aguardam revisão.

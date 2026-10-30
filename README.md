# Patas e Pelos

MVP para organizar as informações de um pequeno negócio de banho e tosa.
O fluxo planejado é **Tutor → Animal → Agendamento → Consulta da agenda**.

## Etapa atual

Etapa 1: estrutura inicial Flask e página de apresentação. Autenticação,
cadastros, agendamentos, banco de dados e GitHub Actions serão implementados
em commits futuros. Os pacotes de regras de negócio e persistência estão vazios.

## Tecnologias

- Python 3.12.
- Flask 3.x e templates Jinja.
- Bootstrap 5.3.8, carregado por CDN com verificação de integridade.
- pytest preparado para testes futuros.
- SQLite planejado para a etapa de persistência; não há banco nesta versão.

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
.\.venv\Scripts\python.exe run.py
```

Abra <http://127.0.0.1:5000>. Para encerrar, pressione `Ctrl+C` no terminal.
O servidor é para desenvolvimento local, limitado ao próprio computador,
com depuração desativada por padrão.

### Alternativa com o Python 3.12 incluído no ambiente Codex desta máquina

Use esta alternativa somente se o executável abaixo existir:

```powershell
& "C:\Users\Leandro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
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
│   ├── config.py
│   ├── presentation/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── services/
│   │   └── __init__.py
│   ├── repositories/
│   │   └── __init__.py
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── static/
│       └── css/
│           └── style.css
└── tests/
    └── .gitkeep
```

- `run.py`: entrada para iniciar o servidor local.
- `app/__init__.py`: função `create_app(test_config=None)`, configuração e registro de rotas.
- `app/config.py`: configurações iniciais, sem credenciais.
- `app/presentation/`: rotas HTTP; templates e arquivos estáticos compõem a interface.
- `app/services/`: regras de negócio futuras.
- `app/repositories/`: persistência futura.
- `tests/` e `pytest.ini`: preparação para testes automatizados.
- `.gitignore`: impede versionar ambientes virtuais, caches, segredos e bancos locais.

## Testes futuros

Quando os testes forem implementados, execute:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Nesta etapa não há testes escritos. Por isso, pytest informa que nenhum teste
foi coletado e retorna código 5; isso não representa uma suíte aprovada.

## Primeiro commit

Revise e versione somente os 15 arquivos apresentados na árvore, incluindo
os arquivos vazios. Não versione `.venv/`, caches, segredos nem dados locais.

```powershell
git init
git add .gitignore README.md requirements.txt run.py pytest.ini app tests/.gitkeep
git status --short
git commit -m "chore: cria estrutura inicial do projeto Flask"
```

Esse comando cria um commit local. O envio ao GitHub depende da criação e
configuração do repositório remoto, que ainda não fazem parte desta etapa.

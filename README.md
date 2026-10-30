# Patas e Pelos

MVP para organizar as informações de um pequeno negócio de banho e tosa.
O fluxo planejado é **Tutor → Animal → Agendamento → Consulta da agenda**.

## Etapa atual

Etapa 5: consolidação da suíte pytest e integração contínua com GitHub Actions.
O MVP mantém autenticação, cadastros de tutores e animais e criação e consulta
de agendamentos, sem novas funcionalidades de negócio nesta etapa.

As quatro primeiras etapas já foram commitadas e enviadas ao
[repositório no GitHub](https://github.com/Leandro97-cmd/patas-e-pelos-mvp):
`1997ba5` (estrutura inicial), `fd43008` (autenticação), `bd8a866` (tutores e animais)
e `d88d152` (agendamentos).

Não há conclusão de atendimento, cancelamento de agendamentos, histórico de
atendimentos, pagamentos, controle financeiro, estoque, emissão fiscal ou mensagens automáticas.
Também não há cadastro público de colaboradores ou recuperação de senha.

## Tecnologias

- Python 3.12.
- Flask 3.x e templates Jinja.
- Bootstrap 5.3.8, carregado por CDN com verificação de integridade.
- SQLite da biblioteca padrão do Python, para colaboradores, tutores, animais e agendamentos.
- Argon2id com `argon2-cffi`, para armazenamento de senhas.
- Flask-WTF para proteção CSRF dos formulários.
- pytest com testes isolados de autenticação, cadastros e agendamentos.
- GitHub Actions para executar a suíte em push e pull request.

As quatro dependências diretas permanecem em um único `requirements.txt`,
incluindo pytest. Para este MVP, um único comando instala o necessário para
desenvolvimento e testes, sem acrescentar arquivos ou ferramentas de gestão.

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

### Atualizar uma instalação anterior

Com o servidor encerrado e a mesma chave de sessão já configurada no terminal,
execute:

```powershell
.\.venv\Scripts\python.exe -m flask --app run init-db
.\.venv\Scripts\python.exe run.py
```

`init-db` acrescenta a tabela `agendamentos` e o índice de conflito de horário,
além de criar tabelas de etapas anteriores que ainda não existam. Não apaga
colaboradores, tutores, animais ou agendamentos já existentes. Não remova o
banco e não recrie seu colaborador.
Se necessário, faça uma cópia privada do banco com o servidor encerrado antes
de atualizar. Caso esteja configurando o projeto pela primeira vez, siga abaixo.

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
`init-db` pode ser executado novamente sem apagar registros existentes.
Proteja o arquivo com as permissões do sistema operacional; SQLite não está
criptografado. Caso precise de backup local, copie o banco com a aplicação
encerrada e mantenha a cópia em local privado.

### 3. Iniciar

```powershell
.\.venv\Scripts\python.exe run.py
```

Abra <http://127.0.0.1:5000>. O sistema direciona para `/login`. Entre com
`demo.local` e a senha que você definiu. Após o login, a página inicial interna
mostra o nome do colaborador, as opções de cadastro e consulta e o botão
**Sair**. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

## Tutores e animais

No menu interno, use **Cadastrar tutor** e depois **Cadastrar animal**.
As opções **Consultar tutores** e **Consultar animais** exibem os registros,
do mais recente para o mais antigo. Cadastros bem-sucedidos redirecionam para
a lista com uma confirmação textual. Atualizar a lista não repete o cadastro.

Rotas internas desta etapa:

| Página | Endereço | Ações |
| --- | --- | --- |
| Lista de tutores | `/tutores` | Consultar os tutores cadastrados |
| Cadastro de tutor | `/tutores/novo` | Exibir e enviar o formulário |
| Lista de animais | `/animais` | Consultar animais com nome e ID do tutor |
| Cadastro de animal | `/animais/novo` | Exibir e enviar o formulário |

### Regras dos tutores

- `id_tutor`: inteiro e chave primária, gerado pelo SQLite.
- Nome obrigatório, com até 100 caracteres. Espaços extras no nome são reduzidos.
- Telefone obrigatório: de 8 a 15 dígitos, com entrada de até 32 caracteres.
  São aceitos números, espaços, parênteses, hífen e `+` inicial. O telefone é
  salvo e exibido somente com dígitos; informe DDD e código do país quando necessário.
- Observações opcionais, com até 2000 caracteres. Valores vazios ficam como `NULL`.
- O mesmo nome e telefone não podem ser cadastrados novamente. A comparação
  ignora maiúsculas, acentos e espaços extras no nome, além da formatação do
  telefone. Uma chave derivada interna, `nome_chave`, permite aplicar a mesma
  regra com uma restrição única no SQLite, inclusive em envios simultâneos.
- Nomes diferentes podem compartilhar telefone; nomes iguais podem ter telefones
  diferentes. Códigos de país não são acrescentados ou removidos automaticamente.
  A regra é simples: não identifica apelidos, mudanças de telefone ou grafias diferentes.

### Regras dos animais

- `id_animal`: inteiro e chave primária, gerado pelo SQLite.
- Nome obrigatório, com até 100 caracteres.
- Espécie obrigatória, com até 60 caracteres; porte obrigatório, com até 30.
  Ambos são textos livres, pois ainda não foi definido um catálogo de categorias.
- Raça opcional, com até 100 caracteres; observações opcionais, com até 2000.
- Tutor obrigatório, escolhido em uma lista com ID, nome e telefone. Sem tutores,
  o formulário orienta a cadastrar um primeiro e desabilita o botão de envio.
- O servidor confirma que o tutor existe. A chave estrangeira do SQLite também
  impede animais sem tutor e a remoção de um tutor referenciado.
- A consulta mostra os dados do animal e o nome e identificador de seu tutor.

Todos os campos são validados no servidor, mesmo quando a validação do navegador
é ignorada. Erros identificam os campos e preservam os dados digitados. As listas
têm indicação de estado vazio e tabelas que podem ser roladas horizontalmente
em telas pequenas, inclusive por teclado.

O limite total de envio é de 64 KiB, suficiente para os campos permitidos,
inclusive textos Unicode. Envios acima desse limite recebem uma mensagem
segura para reduzir o conteúdo.

Não foram adicionadas edição, exclusão, busca avançada ou paginação. As consultas
são listas simples, adequadas ao volume inicial do MVP. Não há CPF, endereço ou
outros dados pessoais adicionais nos cadastros.

## Agendamentos e agenda

No menu interno, use **Novo agendamento** para selecionar o animal e o serviço,
informar data e horário e salvar. Cada opção de animal mostra seu ID, nome e
o ID e nome de seu tutor. Se não houver animais com tutor válido, o formulário
orienta a cadastrá-los antes e desabilita o botão de envio.

As páginas desta etapa são:

| Página | Endereço | Ações |
| --- | --- | --- |
| Agenda | `/agendamentos` | Consultar os registros do banco |
| Novo agendamento | `/agendamentos/novo` | Exibir e enviar o formulário |

### Regras

- `id_agendamento` é uma chave primária inteira gerada pelo SQLite.
- Animal, serviço, data e horário são obrigatórios. O animal e seu tutor precisam
  existir. O agendamento tem chave estrangeira obrigatória para `animais`.
- Serviços permitidos: **Banho**, **Tosa** e **Banho + Tosa**, com validação no
  serviço de negócio e uma restrição `CHECK` no SQLite.
- Novos registros sempre recebem **Agendado** no servidor. Qualquer campo
  `status` adicionado manualmente ao envio é ignorado. O formulário não oferece
  escolha de status.
- O conjunto fechado de status é **Agendado**, **Concluído** e **Cancelado**.
  Os dois últimos estão previstos somente no modelo; não há ações ou telas
  para concluir ou cancelar atendimentos nesta etapa.
- Datas são validadas no calendário e armazenadas em `AAAA-MM-DD`; horários
  são validados e armazenados em `HH:MM`, entre 00:00 e 23:59, com precisão
  de minutos. A agenda exibe datas em `DD/MM/AAAA`.
- Não há restrição de dia da semana, expediente ou data futura. Essas políticas
  ainda não foram definidas; datas passadas válidas também são aceitas.
- Datas e horários representam o horário local do estabelecimento, sem
  conversão de fuso horário.
- Observações são opcionais, com até 2000 caracteres; valores vazios ficam
  como `NULL`. O campo reutiliza o padrão dos cadastros existentes.
- Após salvar, o sistema redireciona para a agenda com confirmação textual.
  Erros identificam os campos e mantêm os dados enviados. O botão de voltar
  descarta o formulário e não cancela registros já salvos.

### Decisão sobre conflitos

O MVP usa **uma agenda única para o estabelecimento**, permitindo somente um
início de atendimento por combinação exata de data e horário, inclusive para
animais diferentes. Um índice único no SQLite aplica a regra mesmo em envios
simultâneos; conflitos recebem uma mensagem compreensível no campo horário.

A regra não calcula duração, intervalos entre serviços, disponibilidade de
profissionais ou capacidade de atendimento simultâneo. Por exemplo, 09:30 e
09:31 são horários distintos e aceitos. Essa limitação é deliberada nesta etapa.

O índice considera registros cujo status não seja `Cancelado`, preparando uma
futura liberação do horário após cancelamento. Isso não acrescenta uma função
de cancelamento à aplicação atual.

### Consulta

A agenda recupera os dados com junções entre agendamento, animal e tutor.
Exibe animal, tutor, serviço, data, horário, status por extenso e observações,
ordenados por data e horário crescentes. Quando não há registros, aparece
“Nenhum agendamento cadastrado”. Há links para novo agendamento e retorno
ao menu, com a mesma navegação, foco e tabela responsiva das demais páginas.

## Segurança e limites desta etapa

- Rotas internas exigem sessão; somente login e arquivos estáticos são públicos.
- Credenciais são validadas no servidor. Login inválido usa sempre a mensagem
  “Usuário ou senha inválidos.”, sem identificar qual campo estava incorreto.
- Sessões são assinadas pelo Flask, com duração de até 8 horas e cookies
  `HttpOnly` e `SameSite=Lax`. A sessão contém identificador de usuário e
  metadados técnicos, sem nome, senha ou hash. Cookies assinados não são cifrados.
- A sessão anterior é limpa ao entrar. O logout exige POST com token CSRF e
  remove a sessão do navegador. As respostas dinâmicas usam `Cache-Control: no-store`.
- Login, logout, cadastros e criação de agendamentos têm proteção CSRF. Jinja escapa os dados exibidos, e as
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
├── .github/
│   └── workflows/
│       └── tests.yml
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
│   │   ├── agendamentos.py
│   │   ├── animais.py
│   │   ├── auth.py
│   │   ├── routes.py
│   │   └── tutores.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agendamentos.py
│   │   ├── animais.py
│   │   ├── auth.py
│   │   ├── tutores.py
│   │   └── validation.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── agendamentos.py
│   │   ├── animais.py
│   │   ├── colaboradores.py
│   │   ├── database.py
│   │   └── tutores.py
│   ├── templates/
│   │   ├── _form_helpers.html
│   │   ├── base.html
│   │   ├── error.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── agendamentos/
│   │   │   ├── form.html
│   │   │   └── list.html
│   │   ├── animais/
│   │   │   ├── form.html
│   │   │   └── list.html
│   │   └── tutores/
│   │       ├── form.html
│   │       └── list.html
│   └── static/
│       └── css/
│           └── style.css
└── tests/
    ├── .gitkeep
    ├── conftest.py
    ├── test_agendamentos.py
    ├── test_auth.py
    └── test_cadastros.py
```

- `run.py`: entrada para iniciar o servidor local.
- `app/__init__.py`: função `create_app(test_config=None)`, configuração e registro de rotas.
- `app/config.py`: configurações iniciais, sem credenciais.
- `app/cli.py`: comandos locais para preparar o banco e criar colaboradores.
- `app/presentation/`: rotas HTTP; templates e arquivos estáticos compõem a interface.
- `app/services/`: regras de cadastro, agendamento, validação e autenticação com Argon2id.
- `app/repositories/`: conexão e persistência SQLite com consultas parametrizadas.
- `tests/` e `pytest.ini`: suíte automatizada por domínio e configuração do pytest.
- `.github/workflows/tests.yml`: execução automática dos testes no GitHub Actions.
- `.gitignore`: impede versionar ambientes virtuais, caches, segredos e bancos locais.

## Testes automatizados

Na pasta do projeto, com o ambiente virtual preparado e Python 3.12, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

O comando executa toda a suíte. Para investigar uma falha com mais detalhes,
use `python -m pytest -v` com o Python do ambiente virtual.

Os testes usam bancos temporários, chaves aleatórias e colaboradores fictícios.
Não é necessário definir `PATAS_SECRET_KEY`, criar um banco real ou configurar
um usuário de demonstração para executar a suíte. CSRF permanece habilitado.

A suíte verifica login válido e inválido, acesso protegido, logout, CSRF,
hashes Argon2id, validação, duplicidade, consultas parametrizadas, escape de
HTML, cookies, usuário removido, chave obrigatória e comandos locais.
Também verifica cadastro e consulta de tutores e animais, campos obrigatórios,
limites, duplicidades, vínculo a tutor, estados vazios, menus, CSRF, acesso sem
autenticação e atualização do banco sem perder os registros da etapa anterior.
Agendamentos têm testes de criação, campos obrigatórios, serviços e status
fechados, datas e horários inválidos, animal e tutor existentes, conflitos,
ordenação, exibição dos relacionamentos, observações, CSRF, autenticação e
atualização do banco preservando os cadastros e agendamentos existentes.

### Organização e cobertura revisada

| Domínio | Arquivo | Comportamentos cobertos |
| --- | --- | --- |
| Autenticação | `tests/test_auth.py` | Login válido e inválido, acesso sem e com autenticação, logout |
| Tutor | `tests/test_cadastros.py` | Cadastro válido, nome e telefone obrigatórios, duplicidade e listagem |
| Animal | `tests/test_cadastros.py` | Cadastro válido, tutor obrigatório e existente, campos obrigatórios e listagem |
| Agendamento | `tests/test_agendamentos.py` | Criação válida, animal obrigatório e existente, serviço obrigatório e permitido, data e horário obrigatórios, conflito, status Agendado e listagem com animal e tutor corretos |

`tests/conftest.py` compartilha as fixtures de aplicação, banco temporário,
credenciais fictícias, cliente HTTP, token CSRF, login e cliente autenticado.
Os auxiliares de envio específicos de cada domínio permanecem em seus arquivos,
para manter os testes fáceis de ler. Nenhum cenário foi adicionado ou removido
nesta consolidação; a suíte possui 178 casos parametrizados.

A suíte automatizada protege contra regressões nos comportamentos verificados.
Isso não substitui a revisão e a conferência manual da interface, nem garante
que todo defeito possível será detectado.

## Integração contínua com GitHub Actions

O workflow está em `.github/workflows/tests.yml`, com o nome
**Testes automatizados**. Ele é disparado em `push` e `pull_request`, sem filtro
de branch, e executa um único job em Ubuntu com Python 3.12:

1. Obtém o código com `actions/checkout`.
2. Configura Python 3.12 com `actions/setup-python` e cache de downloads do pip.
3. Instala as dependências de `requirements.txt`.
4. Executa `python -m pytest -q`, sem ignorar erros.

O job tem limite de 10 minutos e permissão apenas de leitura do conteúdo do
repositório. O checkout não mantém credenciais gravadas na configuração Git.
Não é necessário cadastrar segredos no GitHub: a suíte gera chaves aleatórias
e credenciais fictícias e utiliza bancos temporários por teste. Não acessa o
banco local de demonstração, não inicia um servidor e não publica o sistema.

Após enviar o commit que adiciona o workflow, acompanhe as execuções na aba
[Actions do repositório](https://github.com/Leandro97-cmd/patas-e-pelos-mvp/actions).
Abra **Testes automatizados**, selecione a execução e o job **pytest (Python 3.12)**.

- **Success / sucesso, normalmente verde:** todas as etapas terminaram sem erro.
  A etapa de testes deve mostrar `178 passed` enquanto a suíte permanecer igual.
- **Failure / falha, normalmente vermelho:** alguma etapa falhou. Se for a etapa
  de testes, consulte o nome do teste e a comparação esperada/obtida no log;
  corrija o problema, execute a suíte localmente e envie a correção.
- Falhas de instalação, configuração ou coleta de testes também tornam a
  execução malsucedida. `No tests ran`, execução cancelada ou execução ignorada
  não significam que a suíte passou.

Qualquer teste que falhar faz pytest retornar um código diferente de zero e
reprova o job. O workflow não configura bloqueio de merge: caso desejado no
futuro, isso deve ser definido nas regras do repositório.

A primeira execução remota desta etapa ocorrerá depois do seu commit e push;
a validação local não é uma execução do GitHub Actions.

Referências: [testes Python no GitHub Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python),
[checkout](https://github.com/actions/checkout) e [setup-python](https://github.com/actions/setup-python).

## Próximo commit

Revise as alterações antes de versionar. Não adicione `.venv/`, `instance/`,
chaves, senhas ou bancos locais ao Git.

```powershell
git diff
git add .github/workflows/tests.yml README.md tests/conftest.py tests/test_cadastros.py tests/test_agendamentos.py
git status --short
git commit -m "ci: configura testes automatizados no GitHub Actions"
```

O commit não é feito automaticamente. As próximas funcionalidades aguardam revisão.

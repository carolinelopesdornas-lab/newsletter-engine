# Newsletter JT Esportes

Newsletter semanal automática de educação física. Toda segunda-feira às 7h (horário de Brasília) o sistema busca artigos nas 10 fontes científicas configuradas, processa com a API do Claude e envia um e-mail HTML curado para o destinatário configurado.

Roda 100% na nuvem no **Railway** — não precisa de computador ligado.

---

## Pré-requisitos

| Item | Onde obter |
|---|---|
| Conta no [Railway](https://railway.app) | railway.app |
| Chave de API do Claude | [console.anthropic.com](https://console.anthropic.com) |
| Conta Gmail com **Senha de App** ativada | myaccount.google.com → Segurança → Senhas de app |

---

## Configuração local (para testes)

```bash
# 1. Clone o repositório (ou entre na pasta do projeto)
cd newsletter-jt-esportes

# 2. Crie o ambiente virtual e instale as dependências
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com seus dados reais

# 4. Teste imediatamente (sem esperar segunda-feira)
python scheduler.py --teste
```

---

## Deploy no Railway

### 1. Suba o código

```bash
# Inicialize o Git (se ainda não fez)
git init
git add .
git commit -m "Initial commit"

# Crie um repositório no GitHub e faça o push
git remote add origin https://github.com/SEU_USUARIO/newsletter-jt-esportes.git
git push -u origin main
```

### 2. Crie o projeto no Railway

1. Acesse [railway.app](https://railway.app) e clique em **New Project**
2. Escolha **Deploy from GitHub repo** e selecione o repositório
3. Railway detecta o `railway.json` e configura automaticamente

### 3. Configure as variáveis de ambiente no Railway

No painel do projeto: **Variables** → adicione cada variável:

```
ANTHROPIC_API_KEY   = sk-ant-...
SMTP_HOST           = smtp.gmail.com
SMTP_PORT           = 587
SMTP_USER           = seu_email@gmail.com
SMTP_PASSWORD       = xxxx xxxx xxxx xxxx
FROM_EMAIL          = seu_email@gmail.com
TO_EMAIL            = jtcarvalho.seg@gmail.com
```

### 4. Ative o worker

- Em **Settings** do serviço, confirme que o tipo é **Worker** (não Web)
- Clique em **Deploy** — o container inicia e aguarda a próxima segunda às 7h

---

## Fontes RSS monitoradas

| Fonte | Área |
|---|---|
| PubMed — Strength Training | Treinamento de força e resistência |
| PubMed — Personal Trainer | Metodologia e fitness |
| PubMed — Exercise & Aging | Exercício, gerontologia e longevidade |
| Stronger By Science | Evidências em hipertrofia e força |
| Barbell Medicine | Medicina esportiva e treinamento |
| RP Strength | Periodização e hipertrofia |
| RBPFEX | Pesquisa brasileira em exercício físico |
| RBCE | Revista Brasileira de Ciências do Esporte |
| ACSM | American College of Sports Medicine |
| Science Direct — Exercise | Periódicos acadêmicos internacionais |

---

## Estrutura do projeto

```
newsletter-jt-esportes/
├── main.py            # Lógica principal: RSS → Claude → e-mail
├── scheduler.py       # Agendador APScheduler (ponto de entrada)
├── email_template.py  # Template HTML do e-mail
├── requirements.txt   # Dependências Python
├── .env.example       # Modelo das variáveis de ambiente
├── .env               # Suas credenciais (NÃO commitar)
├── Procfile           # Definição do processo para Railway/Heroku
├── railway.json       # Configuração do Railway
└── README.md          # Esta documentação
```

---

## Comandos úteis

```bash
# Executar imediatamente (modo teste)
python scheduler.py --teste

# Executar só a lógica principal
python main.py

# Ver logs em tempo real (Railway CLI)
railway logs
```

---

## Gmail — Como criar Senha de App

1. Acesse [myaccount.google.com/security](https://myaccount.google.com/security)
2. Ative **Verificação em duas etapas** se ainda não estiver ativa
3. Em "Como você faz login no Google", clique em **Senhas de app**
4. Selecione app **E-mail** e dispositivo **Outro (nome personalizado)** → "Railway Newsletter"
5. Copie a senha de 16 caracteres e use como `SMTP_PASSWORD`

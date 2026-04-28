# Newsletter Engine

Motor de newsletter semanal automática. Busca artigos em fontes RSS, usa o Claude (Anthropic) para curar e resumir o conteúdo, e envia um e-mail HTML formatado para o destinatário configurado.

Cada newsletter é definida por um arquivo JSON em `newsletters/`. O código não precisa ser alterado para criar uma nova.

---

## Como funciona

```
Railway (cron) → main.py → busca RSS → Claude API → envia e-mail
```

1. No horário configurado, o Railway executa `python main.py --newsletter newsletters/<arquivo>.json`
2. O motor busca artigos das fontes RSS definidas no JSON
3. Envia os artigos para o Claude, que gera o conteúdo estruturado da newsletter
4. O e-mail HTML é montado e enviado via SMTP

---

## Estrutura de arquivos

```
newsletter-engine/
├── main.py               # motor principal (não alterar)
├── email_template.py     # template HTML do e-mail (não alterar)
├── scheduler.py          # script para testes locais
├── railway.json          # configuração do Railway
├── Procfile
├── requirements.txt
├── .env.example          # modelo das variáveis de ambiente
└── newsletters/
    ├── jt-esportes.json  # newsletter JT Esportes
    └── <nova>.json       # nova newsletter que você criar
```

---

## Criando uma nova newsletter

### Passo 1 — Criar o arquivo de configuração

Copie `newsletters/jt-esportes.json` como base e edite:

```json
{
  "name": "Nome da Newsletter",
  "from_name": "Nome que aparece no remetente",
  "to_email": "destinatario@email.com",
  "topic": "tema principal da newsletter",
  "audience": "público-alvo (ex: médicos, professores, investidores)",
  "sections": [
    {
      "key": "chave_unica",
      "label": "Título da Seção",
      "emoji": "📌",
      "color": "#CBFF00",
      "instruction": "Instrução para o Claude sobre o que incluir nesta seção."
    }
  ],
  "sources": [
    { "name": "Nome da Fonte", "url": "https://site.com/feed.rss" },
    { "name": "Outra Fonte",   "url": "https://outro.com/feed/", "ignore_http_error": true }
  ]
}
```

**Campos obrigatórios:** `name`, `to_email`, `topic`, `audience`, `sources`

**Opções por fonte:**

| Campo | Descrição |
|---|---|
| `name` | Nome exibido no e-mail |
| `url` | URL do feed RSS/Atom |
| `ignore_http_error` | `true` para ignorar erros HTTP (feeds problemáticos) |
| `verify_ssl` | `false` para ignorar erros de certificado SSL |

**Opções por seção:**

| Campo | Descrição |
|---|---|
| `key` | Chave única (sem espaços), usada no JSON do Claude |
| `label` | Título exibido no e-mail |
| `emoji` | Ícone da seção |
| `color` | Cor hex do título e bordas (ex: `#CBFF00`) |
| `instruction` | Instrução para o Claude sobre o que selecionar |

### Passo 2 — Adicionar um Cron Service no Railway

1. No painel do Railway, abra seu projeto
2. Clique em **New Service → Empty Service**
3. Conecte ao mesmo repositório GitHub
4. Em **Settings → Deploy → Start Command**, coloque:
   ```
   python main.py --newsletter newsletters/<nome-do-arquivo>.json
   ```
5. Em **Settings → Schedule**, defina o horário no formato cron (UTC):
   ```
   0 10 * * 1   → toda segunda às 07h (BRT = UTC-3)
   0 12 * * 5   → toda sexta às 09h (BRT)
   ```
6. Adicione as variáveis de ambiente (mesmas do projeto principal)

---

## Testando localmente

```bash
# Copia o .env.example e preenche com suas credenciais reais
cp .env.example .env

# Instala as dependências
pip install -r requirements.txt

# Dispara a newsletter imediatamente
python scheduler.py --newsletter newsletters/jt-esportes.json
```

---

## Variáveis de ambiente

Configure no Railway em **Settings → Variables** (ou no arquivo `.env` para testes locais):

| Variável | Descrição | Exemplo |
|---|---|---|
| `ANTHROPIC_API_KEY` | Chave da API do Claude | `sk-ant-...` |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SMTP_USER` | E-mail de envio | `seuemail@gmail.com` |
| `SMTP_PASSWORD` | Senha de app do Gmail | `xxxx xxxx xxxx xxxx` |
| `FROM_EMAIL` | Remetente (igual ao SMTP_USER) | `seuemail@gmail.com` |

> **Gmail:** crie uma "Senha de app" em [myaccount.google.com/security](https://myaccount.google.com/security). Requer verificação em duas etapas ativada.

---

## Seções fixas (sempre presentes)

Além das seções que você define no JSON, toda newsletter inclui automaticamente:

- **Destaque da Semana** — artigo mais relevante com aplicação prática
- **Dicas para sua Prática** — 3 dicas geradas pelo Claude
- **Reflexão da Semana** — citação ou insight motivacional
- **Resumo Executivo** — parágrafo no cabeçalho com os principais aprendizados

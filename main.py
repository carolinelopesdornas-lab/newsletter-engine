import os
import sys
import json
import logging
import smtplib
import feedparser
import requests
import urllib3
import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from anthropic import Anthropic
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email_template import gerar_html_email

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

FONTES_RSS = [
    {
        "nome": "International Journal of Exercise Science",
        "url": "https://digitalcommons.wku.edu/ijes/recent.rss",
    },
    {
        "nome": "Sigma Nutrition",
        "url": "https://sigmanutrition.com/feed/",
    },
    {
        "nome": "Frontiers in Sports and Active Living",
        "url": "https://www.frontiersin.org/journals/sports-and-active-living/rss",
    },
    {
        "nome": "Stronger By Science",
        "url": "https://www.strongerbyscience.com/feed/",
    },
    {
        "nome": "Barbell Medicine",
        "url": "https://www.barbellmedicine.com/blog/feed/",
    },
    {
        "nome": "Science for Sport",
        "url": "https://www.scienceforsport.com/feed/",
    },
    {
        "nome": "RBPFEX",
        "url": "https://www.rbpfex.com.br/index.php/rbpfex/gateway/plugin/WebFeedGatewayPlugin/rss2",
    },
    {
        "nome": "Peter Attia - The Drive",
        "url": "https://peterattiamd.com/feed/",
    },
    {
        "nome": "RP Strength (Dr. Mike Israetel)",
        "url": "https://rpstrength.com/blogs/articles.atom",
    },
    {
        "nome": "Tênis Certo (YouTube)",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCaVpzaxGCCrNgZt5l4lh5OA",
    },
    {
        "nome": "Dave Asprey - Biohacking",
        "url": "https://daveasprey.com/feed/",
    },
    {
        "nome": "Ben Greenfield Life",
        "url": "https://bengreenfieldlife.com/feed/",
        "ignore_http_error": True,
    },
    {
        "nome": "DC Rainmaker",
        "url": "https://www.dcrainmaker.com/feed",
    },
    {
        "nome": "Wareable",
        "url": "https://www.wareable.com/feed/",
    },
    {
        "nome": "Science Direct - Exercise Science",
        "url": "https://rss.sciencedirect.com/publication/science/07651597",
    },
]

HEADERS_HTTP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _extrair_texto(html_str: str, limite: int = 500) -> str:
    if not html_str:
        return ""
    try:
        soup = BeautifulSoup(html_str, "lxml")
        return soup.get_text(separator=" ", strip=True)[:limite]
    except Exception:
        return html_str[:limite]


def _data_entry(entry) -> datetime | None:
    tz_utc = timezone.utc
    for attr in ("published_parsed", "updated_parsed"):
        tupla = getattr(entry, attr, None)
        if tupla:
            try:
                return datetime(*tupla[:6], tzinfo=tz_utc)
            except Exception:
                continue
    return None


def buscar_artigos_rss() -> list[dict]:
    """Busca artigos de todas as fontes RSS. Inclui os mais recentes de cada fonte."""
    tz_sp = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz_sp)
    limite_7d = agora - timedelta(days=7)

    logger.info(
        "Buscando artigos publicados desde %s",
        limite_7d.strftime("%d/%m/%Y %H:%M"),
    )

    todos: list[dict] = []

    for fonte in FONTES_RSS:
        try:
            logger.info("Acessando feed: %s", fonte["nome"])
            verify = fonte.get("verify_ssl", True)
            resp = requests.get(fonte["url"], headers=HEADERS_HTTP, timeout=30, verify=verify)
            if not fonte.get("ignore_http_error", False):
                resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            if feed.bozo:
                logger.warning(
                    "Feed mal-formado em '%s' — tentando mesmo assim", fonte["nome"]
                )

            artigos_fonte: list[dict] = []
            sem_data: list[dict] = []

            for entry in feed.entries:
                titulo = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                if not titulo or not link:
                    continue

                resumo_raw = (
                    getattr(entry, "summary", None)
                    or getattr(entry, "description", None)
                    or (
                        entry.content[0].get("value", "")
                        if getattr(entry, "content", None)
                        else ""
                    )
                )
                resumo = _extrair_texto(resumo_raw, 600)

                data_utc = _data_entry(entry)

                artigo = {
                    "titulo": titulo,
                    "link": link,
                    "resumo": resumo,
                    "fonte": fonte["nome"],
                    "data_utc": data_utc,
                    "data": (
                        data_utc.astimezone(tz_sp).strftime("%d/%m/%Y")
                        if data_utc
                        else "Data não informada"
                    ),
                }

                if data_utc is None:
                    sem_data.append(artigo)
                elif data_utc.astimezone(tz_sp) >= limite_7d:
                    artigos_fonte.append(artigo)

            # Garante pelo menos 3 artigos por fonte (sem data ou mais antigos)
            if len(artigos_fonte) < 3:
                for a in sem_data[: 3 - len(artigos_fonte)]:
                    artigos_fonte.append(a)

            todos.extend(artigos_fonte)
            logger.info(
                "  ✓ %s: %d artigos selecionados", fonte["nome"], len(artigos_fonte)
            )

        except requests.RequestException as exc:
            logger.error("Erro de rede em '%s': %s", fonte["nome"], exc)
        except Exception as exc:
            logger.error("Erro inesperado em '%s': %s", fonte["nome"], exc, exc_info=True)

    todos.sort(
        key=lambda a: a["data_utc"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    logger.info("Total de artigos coletados: %d", len(todos))
    return todos


def processar_com_claude(artigos: list[dict]) -> dict | None:
    """Envia os artigos ao Claude e recebe o conteúdo estruturado da newsletter."""
    if not artigos:
        logger.warning("Nenhum artigo disponível para processamento")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY não configurada nas variáveis de ambiente")

    client = Anthropic(api_key=api_key)

    linhas: list[str] = []
    for i, a in enumerate(artigos[:50], 1):
        linhas.append(
            f"{i}. TÍTULO: {a['titulo']}\n"
            f"   FONTE: {a['fonte']}\n"
            f"   DATA: {a['data']}\n"
            f"   LINK: {a['link']}\n"
            f"   RESUMO: {a['resumo'][:400]}\n"
        )
    artigos_fmt = "\n".join(linhas)

    prompt = f"""Você é um especialista em educação física, treinamento de força e ciência do exercício.
Analise os artigos abaixo e crie uma newsletter semanal em PORTUGUÊS do Brasil para profissionais de educação física e personal trainers.

ARTIGOS DISPONÍVEIS:
{artigos_fmt}

Crie uma newsletter com a estrutura JSON abaixo. Responda APENAS com JSON válido, sem blocos de código markdown.

{{
    "destaque_semana": {{
        "titulo": "título do artigo mais relevante (traduzido se necessário)",
        "fonte": "nome da fonte",
        "link": "url exato do artigo",
        "resumo": "resumo em 3-4 frases sobre a importância do estudo",
        "aplicacao_pratica": "como aplicar na prática com clientes em 2-3 frases"
    }},
    "artigos_pesquisa": [
        {{
            "titulo": "título em português",
            "fonte": "nome da fonte",
            "link": "url exato",
            "data": "data de publicação conforme informado (ex: 23/04/2026 ou Data não informada)",
            "resumo": "2-3 frases sobre o estudo em português",
            "relevancia": "alta | media | baixa"
        }}
    ],
    "dicas_praticas": [
        {{
            "titulo": "título objetivo da dica",
            "conteudo": "dica prática baseada nos artigos, 2-3 frases"
        }}
    ],
    "noticias_tenis": [
        {{
            "titulo": "título do vídeo/artigo",
            "fonte": "nome da fonte",
            "link": "url exato",
            "data": "data de publicação conforme informado",
            "resumo": "2-3 frases descrevendo o conteúdo"
        }}
    ],
    "biohacking": [
        {{
            "titulo": "título em português",
            "fonte": "nome da fonte",
            "link": "url exato",
            "data": "data de publicação conforme informado",
            "resumo": "2-3 frases sobre o conteúdo de biohacking"
        }}
    ],
    "tecnologia_vestiveis": [
        {{
            "titulo": "título em português",
            "fonte": "nome da fonte",
            "link": "url exato",
            "data": "data de publicação conforme informado",
            "resumo": "2-3 frases sobre o produto ou tecnologia"
        }}
    ],
    "frase_semana": "citação ou insight motivacional relacionado aos temas",
    "resumo_executivo": "parágrafo de 4-5 frases com os principais aprendizados da semana"
}}

Regras:
- Selecione os 5 a 8 artigos mais relevantes para treinamento de força e personal training em "artigos_pesquisa"
- Crie exatamente 3 dicas práticas aplicáveis ao dia a dia
- Priorize em artigos_pesquisa: hipertrofia, força, periodização, longevidade, nutrição, biohacking
- Em "noticias_tenis": inclua exatamente 3 itens da fonte "Tênis Certo (YouTube)", os mais recentes
- Em "biohacking": inclua 3-5 itens das fontes "Dave Asprey - Biohacking" e "Ben Greenfield Life"; se não houver, use qualquer artigo sobre biohacking, otimização humana, longevidade ou suplementação
- Em "tecnologia_vestiveis": inclua itens das fontes "DC Rainmaker" e "Wareable", no mínimo 3; se não houver, use qualquer artigo sobre tecnologia, wearables ou equipamentos esportivos
- Responda SOMENTE com JSON válido"""

    logger.info("Enviando %d artigos ao Claude para curadoria...", len(artigos[:50]))

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        resposta = message.content[0].text.strip()

        # Remove blocos markdown se presentes
        if resposta.startswith("```"):
            linhas_r = resposta.split("\n")
            resposta = "\n".join(linhas_r[1:]).rstrip("`").strip()

        conteudo = json.loads(resposta)
        logger.info("Conteúdo da newsletter gerado com sucesso pelo Claude")
        return conteudo

    except json.JSONDecodeError as exc:
        logger.error("Resposta do Claude não é JSON válido: %s", exc)
        logger.error("Trecho da resposta: %.300s", resposta)
        return None
    except Exception as exc:
        logger.error("Erro ao chamar API do Claude: %s", exc, exc_info=True)
        return None


def enviar_email(conteudo: dict, data_envio: datetime) -> None:
    """Monta e envia o e-mail HTML da newsletter via SMTP."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    from_email = os.environ.get("FROM_EMAIL", smtp_user)
    to_email = os.environ.get("TO_EMAIL", "jtcarvalho.seg@gmail.com")

    if not smtp_user or not smtp_password:
        raise ValueError(
            "Credenciais SMTP ausentes. Configure SMTP_USER e SMTP_PASSWORD."
        )

    html_content = gerar_html_email(conteudo, data_envio)
    data_str = data_envio.strftime("%d/%m/%Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Newsletter JT Esportes — Semana de {data_str}"
    msg["From"] = f"JT Esportes Newsletter <{from_email}>"
    msg["To"] = to_email

    destaque_titulo = conteudo.get("destaque_semana", {}).get("titulo", "")
    texto_plain = (
        f"Newsletter JT Esportes — {data_str}\n\n"
        f"Destaque da semana: {destaque_titulo}\n\n"
        "Abra este e-mail em um cliente com suporte a HTML para a melhor experiência."
    )

    msg.attach(MIMEText(texto_plain, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    logger.info("Conectando ao servidor SMTP %s:%d...", smtp_host, smtp_port)
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, [to_email], msg.as_string())

    logger.info("E-mail enviado com sucesso para %s", to_email)


def executar_newsletter() -> bool:
    """Orquestra todo o fluxo: busca RSS → Claude → envio de e-mail."""
    tz_sp = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz_sp)

    logger.info("=" * 60)
    logger.info(
        "INICIANDO NEWSLETTER JT ESPORTES — %s", agora.strftime("%d/%m/%Y %H:%M")
    )
    logger.info("=" * 60)

    try:
        logger.info("[ ETAPA 1/3 ] Buscando artigos nas fontes RSS...")
        artigos = buscar_artigos_rss()

        if not artigos:
            logger.warning("Nenhum artigo encontrado. Execução encerrada.")
            return False

        logger.info("[ ETAPA 2/3 ] Processando artigos com Claude...")
        conteudo = processar_com_claude(artigos)

        if not conteudo:
            logger.error("Falha no processamento com Claude. Execução encerrada.")
            return False

        logger.info("[ ETAPA 3/3 ] Enviando e-mail...")
        enviar_email(conteudo, agora)

        logger.info("=" * 60)
        logger.info("NEWSLETTER ENVIADA COM SUCESSO!")
        logger.info("=" * 60)
        return True

    except Exception as exc:
        logger.error("Erro fatal: %s", exc, exc_info=True)
        return False


if __name__ == "__main__":
    sucesso = executar_newsletter()
    sys.exit(0 if sucesso else 1)

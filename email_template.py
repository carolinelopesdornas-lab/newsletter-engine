from datetime import datetime

_MESES_PT = {
    "January": "Janeiro", "February": "Fevereiro", "March": "Março",
    "April": "Abril", "May": "Maio", "June": "Junho",
    "July": "Julho", "August": "Agosto", "September": "Setembro",
    "October": "Outubro", "November": "Novembro", "December": "Dezembro",
}

_COR_RELEVANCIA = {
    "alta": "#CBFF00",
    "media": "#00BFFF",
    "baixa": "#4a5568",
}

_COR_TEXTO_RELEVANCIA = {
    "alta": "#0E1933",
    "media": "#0E1933",
    "baixa": "#ffffff",
}

_ICONES_DICAS = ["💪", "🎯", "📊", "🏋️", "⚡"]


def _data_pt(dt: datetime) -> str:
    s = dt.strftime("%d de %B de %Y")
    for en, pt in _MESES_PT.items():
        s = s.replace(en, pt)
    return s


def _barras_graficas() -> str:
    return """
    <table width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 22px;">
      <tr><td style="padding-bottom:5px;">
        <table width="72%" cellpadding="0" cellspacing="0"><tr><td style="background:#00BFFF;height:4px;border-radius:2px;font-size:1px;line-height:1px;">&nbsp;</td></tr></table>
      </td></tr>
      <tr><td style="padding-bottom:5px;">
        <table width="42%" cellpadding="0" cellspacing="0"><tr><td style="background:#0099cc;height:4px;border-radius:2px;font-size:1px;line-height:1px;">&nbsp;</td></tr></table>
      </td></tr>
      <tr><td style="padding-bottom:5px;">
        <table width="86%" cellpadding="0" cellspacing="0"><tr><td style="background:#007aa3;height:4px;border-radius:2px;font-size:1px;line-height:1px;">&nbsp;</td></tr></table>
      </td></tr>
      <tr><td style="padding-bottom:5px;">
        <table width="28%" cellpadding="0" cellspacing="0"><tr><td style="background:#CBFF00;height:4px;border-radius:2px;font-size:1px;line-height:1px;">&nbsp;</td></tr></table>
      </td></tr>
      <tr><td>
        <table width="55%" cellpadding="0" cellspacing="0"><tr><td style="background:#00BFFF;height:4px;border-radius:2px;font-size:1px;line-height:1px;">&nbsp;</td></tr></table>
      </td></tr>
    </table>"""


def _html_secao_lista(itens: list[dict], cor: str) -> str:
    blocos: list[str] = []
    for i, a in enumerate(itens, 1):
        relevancia = str(a.get("relevancia", "")).lower()
        data_str = a.get("data", "")

        badge = ""
        if relevancia in _COR_RELEVANCIA:
            cor_badge = _COR_RELEVANCIA[relevancia]
            cor_texto_badge = _COR_TEXTO_RELEVANCIA[relevancia]
            badge = f'<span style="background:{cor_badge};color:{cor_texto_badge};font-size:10px;font-weight:bold;padding:3px 8px;border-radius:3px;letter-spacing:0.5px;">{relevancia.upper()}</span>&nbsp;'

        blocos.append(f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;border-left:3px solid {cor};background:#132040;border-radius:0 8px 8px 0;">
          <tr>
            <td style="padding:16px 18px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>{badge}<span style="font-size:11px;color:rgba(255,255,255,0.4);">{data_str}</span></td>
                  <td align="right"><span style="font-size:11px;color:rgba(255,255,255,0.35);">{a.get('fonte','')}</span></td>
                </tr>
              </table>
              <h3 style="margin:10px 0 8px;font-size:14px;line-height:1.45;">
                <span style="color:{cor};font-weight:900;font-size:12px;">#{i}</span>&nbsp;<a href="{a.get('link','#')}" style="color:#ffffff;text-decoration:none;font-weight:600;">{a.get('titulo','')}</a>
              </h3>
              <p style="margin:0 0 10px;font-size:12px;color:rgba(255,255,255,0.65);line-height:1.7;">{a.get('resumo','')}</p>
              <a href="{a.get('link','#')}" style="font-size:11px;font-weight:bold;color:{cor};text-decoration:none;letter-spacing:0.5px;">LER →</a>
            </td>
          </tr>
        </table>""")
    return "\n".join(blocos)


def _html_dicas(dicas: list[dict]) -> str:
    blocos: list[str] = []
    for i, d in enumerate(dicas):
        icone = _ICONES_DICAS[i % len(_ICONES_DICAS)]
        blocos.append(f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px;background:#132040;border-radius:6px;border-top:3px solid #CBFF00;">
          <tr>
            <td style="padding:18px 20px;">
              <p style="margin:0 0 8px;font-size:14px;font-weight:bold;color:#CBFF00;">{icone}&nbsp; {d.get('titulo','')}</p>
              <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.72);line-height:1.75;">{d.get('conteudo','')}</p>
            </td>
          </tr>
        </table>""")
    return "\n".join(blocos)


def gerar_html_email(conteudo: dict, config: dict, data_envio: datetime) -> str:
    data_fmt = _data_pt(data_envio)
    data_curta = data_envio.strftime("%d.%m.%Y")
    nome = config.get("name", "Newsletter")
    barras = _barras_graficas()

    destaque = conteudo.get("destaque_semana", {})
    dicas = conteudo.get("dicas_praticas", [])
    frase = conteudo.get("frase_semana", "")
    resumo = conteudo.get("resumo_executivo", "")
    dicas_html = _html_dicas(dicas)

    secoes_html = ""
    for s in config.get("sections", []):
        itens = conteudo.get(s["key"], [])
        if itens:
            cor = s.get("color", "#CBFF00")
            secoes_html += f"""
      {barras}
      <p style="margin:0 0 14px;font-size:10px;font-weight:bold;letter-spacing:3px;color:{cor};text-transform:uppercase;">{s.get('emoji','📄')} &nbsp;{s['label']}</p>
      {_html_secao_lista(itens, cor)}
"""

    fontes_nomes = " · ".join(s["name"] for s in config.get("sources", [])[:10])

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{nome} — {data_fmt}</title>
</head>
<body style="margin:0;padding:0;background:#060d1a;font-family:Arial,'Helvetica Neue',sans-serif;color:#ffffff;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#060d1a;">
<tr><td align="center" style="padding:24px 16px;">

  <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

    <!-- FAIXA COLORIDA -->
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="58%" style="background:#00BFFF;height:5px;font-size:1px;line-height:1px;">&nbsp;</td>
          <td width="28%" style="background:#CBFF00;height:5px;font-size:1px;line-height:1px;">&nbsp;</td>
          <td style="background:#0E1933;height:5px;font-size:1px;line-height:1px;">&nbsp;</td>
        </tr>
      </table>
    </td></tr>

    <!-- BARRA DE NAVEGAÇÃO -->
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0E1933;">
        <tr><td style="padding:13px 24px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="font-size:13px;font-weight:900;color:#ffffff;letter-spacing:2px;">{nome.upper()}</td>
              <td align="right">
                <span style="font-size:10px;font-weight:bold;color:#CBFF00;letter-spacing:1px;">EDIÇÃO {data_curta}</span>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </td></tr>

    <!-- HERO -->
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#CBFF00;">
        <tr><td style="padding:40px 32px 32px;">
          <p style="margin:0 0 8px;font-size:10px;font-weight:bold;letter-spacing:4px;color:#0E1933;text-transform:uppercase;">Newsletter Semanal</p>
          <h1 style="margin:0 0 4px;font-size:52px;font-weight:900;color:#ffffff;letter-spacing:-2px;line-height:1;">{nome.upper()}</h1>
          <p style="margin:0 0 22px;font-size:13px;font-weight:600;color:#0E1933;letter-spacing:1px;text-transform:uppercase;">{config.get('topic','').title()}</p>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#0E1933;border-radius:6px;">
            <tr><td style="padding:16px 20px;">
              <p style="margin:0 0 6px;font-size:10px;font-weight:bold;letter-spacing:2px;color:#CBFF00;text-transform:uppercase;">📋 Esta Semana</p>
              <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.85);line-height:1.7;">{resumo}</p>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </td></tr>

    <!-- CONTEÚDO PRINCIPAL -->
    <tr><td style="background:#0E1933;padding:28px 24px 8px;">

      {barras}

      <!-- DESTAQUE DA SEMANA -->
      <p style="margin:0 0 14px;font-size:10px;font-weight:bold;letter-spacing:3px;color:#CBFF00;text-transform:uppercase;">⭐ &nbsp;Destaque da Semana</p>

      <table width="100%" cellpadding="0" cellspacing="0" style="background:#132040;border-radius:8px;margin-bottom:28px;border-top:3px solid #CBFF00;">
        <tr><td style="padding:24px 22px;">
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;">
            <tr>
              <td><span style="background:#CBFF00;color:#0E1933;font-size:10px;font-weight:bold;padding:4px 10px;border-radius:3px;letter-spacing:1px;">DESTAQUE</span></td>
              <td align="right"><span style="font-size:11px;color:rgba(255,255,255,0.4);">{destaque.get('fonte','')}</span></td>
            </tr>
          </table>
          <h2 style="margin:0 0 12px;font-size:19px;line-height:1.4;font-weight:800;color:#ffffff;">
            <a href="{destaque.get('link','#')}" style="color:#ffffff;text-decoration:none;">{destaque.get('titulo','')}</a>
          </h2>
          <p style="margin:0 0 18px;font-size:13px;color:rgba(255,255,255,0.72);line-height:1.75;">{destaque.get('resumo','')}</p>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:#0E1933;border-left:3px solid #00BFFF;border-radius:0 6px 6px 0;margin-bottom:20px;">
            <tr><td style="padding:14px 16px;">
              <p style="margin:0 0 6px;font-size:10px;font-weight:bold;color:#00BFFF;letter-spacing:2px;text-transform:uppercase;">💡 Aplicação Prática</p>
              <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.80);line-height:1.65;">{destaque.get('aplicacao_pratica','')}</p>
            </td></tr>
          </table>
          <table cellpadding="0" cellspacing="0">
            <tr>
              <td style="background:#CBFF00;border-radius:4px;padding:11px 22px;">
                <a href="{destaque.get('link','#')}" style="font-size:12px;font-weight:900;color:#0E1933;text-decoration:none;letter-spacing:1px;text-transform:uppercase;">Ler Artigo Completo →</a>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>

      <!-- SEÇÕES DINÂMICAS -->
      {secoes_html}

      {barras}

      <!-- DICAS PRÁTICAS -->
      <p style="margin:0 0 14px;font-size:10px;font-weight:bold;letter-spacing:3px;color:#CBFF00;text-transform:uppercase;">💡 &nbsp;Dicas para sua Prática</p>
      {dicas_html}

      <!-- REFLEXÃO DA SEMANA -->
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#132040;border-radius:6px;margin:20px 0 28px;border-left:4px solid #00BFFF;">
        <tr><td style="padding:22px 24px;">
          <p style="margin:0 0 8px;font-size:10px;font-weight:bold;letter-spacing:2px;color:#00BFFF;text-transform:uppercase;">💭 Reflexão da Semana</p>
          <p style="margin:0;font-size:15px;font-style:italic;color:rgba(255,255,255,0.88);line-height:1.75;">"{frase}"</p>
        </td></tr>
      </table>

    </td></tr>

    <!-- RODAPÉ -->
    <tr><td>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="68%" style="background:#00BFFF;height:3px;font-size:1px;line-height:1px;">&nbsp;</td>
          <td style="background:#CBFF00;height:3px;font-size:1px;line-height:1px;">&nbsp;</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0E1933;">
        <tr><td style="padding:22px 24px;text-align:center;">
          <p style="margin:0 0 4px;font-size:16px;font-weight:900;color:#ffffff;letter-spacing:2px;">{nome.upper()}</p>
          <p style="margin:0 0 14px;font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:2px;text-transform:uppercase;">Newsletter Automática · {data_fmt}</p>
          <p style="margin:0;font-size:10px;color:rgba(255,255,255,0.22);line-height:2;">{fontes_nomes}</p>
        </td></tr>
      </table>
    </td></tr>

  </table>
</td></tr>
</table>

</body>
</html>"""

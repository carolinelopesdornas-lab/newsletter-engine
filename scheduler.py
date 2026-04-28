"""
Ponto de entrada do processo contínuo no Railway.

Uso:
  python scheduler.py           → agenda execução toda segunda às 7h (Brasília)
  python scheduler.py --teste   → executa a newsletter imediatamente e encerra
"""

import sys
import logging
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from main import executar_newsletter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

TZ_SP = pytz.timezone("America/Sao_Paulo")


def iniciar_agendador() -> None:
    """Inicia o scheduler bloqueante — executa toda segunda-feira às 07:00 BRT."""
    scheduler = BlockingScheduler(timezone=TZ_SP)

    trigger = CronTrigger(
        day_of_week="mon",
        hour=7,
        minute=0,
        timezone=TZ_SP,
    )

    scheduler.add_job(
        executar_newsletter,
        trigger=trigger,
        id="newsletter_semanal",
        name="Newsletter Semanal JT Esportes",
        replace_existing=True,
        misfire_grace_time=3600,  # tolera até 1 h de atraso (ex: restart do container)
        coalesce=True,            # não executa várias vezes se perdeu múltiplos disparos
    )

    logger.info("=" * 60)
    logger.info("AGENDADOR JT ESPORTES INICIADO")
    logger.info("Próxima execução: toda segunda-feira às 07:00 (Horário de Brasília)")
    logger.info("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agendador encerrado.")
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    if "--teste" in sys.argv:
        logger.info(">>> MODO TESTE: executando newsletter imediatamente <<<")
        sucesso = executar_newsletter()
        sys.exit(0 if sucesso else 1)
    else:
        iniciar_agendador()

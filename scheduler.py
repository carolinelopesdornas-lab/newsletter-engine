"""Uso local para testar a newsletter sem precisar do Railway.

  python scheduler.py --newsletter newsletters/jt-esportes.json
"""
import sys
import argparse
import logging
from main import executar_newsletter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teste local da newsletter")
    parser.add_argument(
        "--newsletter",
        required=True,
        help="Caminho para o arquivo de configuração (ex: newsletters/jt-esportes.json)",
    )
    args = parser.parse_args()
    logger.info(">>> MODO TESTE: executando newsletter imediatamente <<<")
    sucesso = executar_newsletter(args.newsletter)
    sys.exit(0 if sucesso else 1)

import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)

logger = logging.getLogger("abogado_bot")
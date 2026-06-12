import logging
from pathlib import Path


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")


def setup_consumer_file_log() -> None:
    """Файловый лог для Kafka consumer (Демострация работы handlers)."""
    log_path = Path("logs/kafka_consumer.log")
    log_path.parent.mkdir(exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    consumer_logger = logging.getLogger("kafka.consumer")
    consumer_logger.addHandler(handler)
    consumer_logger.setLevel(logging.INFO)

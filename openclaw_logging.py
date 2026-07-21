# Compatibility shim for openclaw_logging (OpenClaw removed 2026-07-10)
import logging
import os

def setup_skill_logger(name):
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger

import uuid
from datetime import datetime

class ExecutionContext:
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.execution_id = str(uuid.uuid4())[:8]
        self._start = datetime.now()
        self._phases = []

    class PhaseCtx:
        def __init__(self, name):
            self.name = name
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def phase(self, name):
        return self.PhaseCtx(name)

    def finalize(self):
        return {'total_duration': (datetime.now() - self._start).total_seconds(), 'execution_id': self.execution_id}

    def log_error(self, msg, exc=None):
        self.logger.error(msg)

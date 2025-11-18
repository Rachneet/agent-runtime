import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

try:
    # optional structured logger
    from pythonjsonlogger import jsonlogger  # type: ignore
    _HAS_JSONLOGGER = True
except Exception:
    _HAS_JSONLOGGER = False


def setup_logging(
    log_level: str = 'INFO',
    log_file: str = 'app.log',
    service_name: str = 'riverty_service',
    to_stdout: Optional[bool] = None,
    force_reload: bool = False,
):
    """Configure centralized logging for the entire application.

    Improvements over the previous implementation:
    - Idempotent: repeated calls won't add duplicate handlers unless `force_reload` is True.
    - File handler uses explicit append mode and path is converted to string.
    - Optional JSON formatting if `python-json-logger` is installed.
    - `to_stdout` override to prefer stdout-only logging (useful in containers).
    """

    logger = logging.getLogger(service_name)
    # If logger already configured and not forcing reload, return it to avoid
    # duplicate handlers or accidental truncation.
    if logger.handlers and not force_reload:
        return logger

    # Create logs directory if it doesn't exist
    log_path = Path('logs')
    log_path.mkdir(parents=True, exist_ok=True)

    # Decide whether to log to stdout only. Environment variable LOG_TO_STDOUT
    # can override default behavior. If `to_stdout` is explicitly provided it wins.
    env_to_stdout = os.getenv('LOG_TO_STDOUT')
    if to_stdout is None:
        to_stdout = (env_to_stdout is not None and env_to_stdout.lower() in ("1", "true", "yes"))

    # Choose formatter: JSON if available and requested via env var
    env_json = os.getenv('LOG_JSON')
    use_json = _HAS_JSONLOGGER and (env_json is not None and env_json.lower() in ("1", "true", "yes"))

    if use_json:
        # Configure a basic json formatter template
        json_fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        # We'll reference the formatter by name in dictConfig below; however
        # fallback to text format if jsonlogger isn't available at runtime.
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s [%(process)d] (%(filename)s:%(funcName)s:%(lineno)d): %(message)s'
            }
        },
        'handlers': {},
        'loggers': {
            '': {  # root logger
                'handlers': [],
                'level': log_level,
                'propagate': False
            },
            service_name: {
                'handlers': [],
                'level': log_level,
                'propagate': False
            }
        }
    }

    # Console handler (stdout)
    if to_stdout:
        logging_config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'standard' if not use_json else 'json',
            'stream': 'ext://sys.stdout'
        }
        logging_config['loggers']['']['handlers'].append('console')
        logging_config['loggers'][service_name]['handlers'].append('console')
    else:
        # Always include a console handler in non-container mode for convenience
        logging_config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
        logging_config['loggers']['']['handlers'].append('console')
        logging_config['loggers'][service_name]['handlers'].append('console')

        # File handler (append mode)
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'detailed',
            'filename': str(log_path / log_file),
            'mode': 'a',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
        logging_config['loggers']['']['handlers'].append('file')
        logging_config['loggers'][service_name]['handlers'].append('file')

    # If json logging is enabled, register a json formatter name. We add it here
    # because it requires a runtime object rather than static dict when using
    # python-json-logger.
    if use_json:
        # Add a simple name so dictConfig will reference it; actual object will be
        # attached after dictConfig if necessary.
        logging_config['formatters']['json'] = {'()': 'pythonjsonlogger.jsonlogger.JsonFormatter', 'fmt': '%(asctime)s %(levelname)s %(name)s %(message)s'}

    logging.config.dictConfig(logging_config)

    # If we have attached a json formatter object earlier (fallback), ensure it's used
    # This is mostly defensive; dictConfig will load pythonjsonlogger if available.

    return logging.getLogger(service_name)
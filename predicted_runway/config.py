import os
from pathlib import Path

LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG"
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "class": "logging.Formatter"
        }
    },
    "disable_existing_loggers": False,
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console"
        ]
    },
    "loggers": {
        "met_update_db": {
            "level": "INFO"
        },
    }
}


DESTINATION_ICAOS = [
    'EHAM',
    'LEMD',
    'LFPO',
    'LOWW'
]

MONGO = {
  "db": os.getenv("MET_UPDATE_DB_NAME", "met-update"),
  "host": "localhost",
  "port": 27017
}

BASE_DIR = Path(__file__).parent

METEO_DIR = Path(os.getenv("MET_UPDATE_DIR", "/data/met"))

RUNWAY_MODELS_DIR = Path("/data/models/runway")
RUNWAY_CONFIG_MODELS_DIR = Path("/data/models/runway_config")

RUNWAY_MODEL_STATS_DIR = Path("/data/stats/runway")
RUNWAY_CONFIG_MODEL_STATS_DIR = Path("/data/stats/runway_config")

ICAO_AIRPORTS_CATALOG_PATH = BASE_DIR.joinpath('static/data').joinpath('icao_airports_catalog.json')

TEMPLATES_DIR = BASE_DIR.joinpath('templates')


def get_runway_model_path(airport_icao: str) -> Path:
    return RUNWAY_MODELS_DIR.joinpath(f'{airport_icao}.pkl').absolute()


def get_runway_config_model_path(airport_icao: str) -> Path:
    return RUNWAY_CONFIG_MODELS_DIR.joinpath(f'{airport_icao}.pkl').absolute()
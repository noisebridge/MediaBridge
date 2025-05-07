from typing import Dict, Type

from flask import Config

from mediabridge.definitions import SQL_CONNECT_STRING


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(BaseConfig):
    # No production database at the moment.
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = SQL_CONNECT_STRING
    DEBUG = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


ENV_TO_CONFIG: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

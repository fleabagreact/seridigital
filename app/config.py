import os
basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "PMtvTKVVscwYg710KMQRYNcKrsDRDurgqbAllO0yxII")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'database/meubanco.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

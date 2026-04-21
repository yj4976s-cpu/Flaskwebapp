import os
from pathlib import Path

basedir = Path(__file__).parent.parent.parent


class LocalConfig:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'images.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INCLUDED_EXTENSION = [".png", ".jpg"]
    DIR_NAME = "handwriting_pics"

config = {
    "local": LocalConfig,
}

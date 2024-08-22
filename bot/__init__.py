from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from bot.utils.logger import Logger
import os

load_dotenv('config.env')
LOG_FILE = os.getenv('LOG_FILE')
RECORDING_PATH = os.path.join(os.getcwd(), os.getenv('RECORDING_FOLDER', 'recordings'))
os.makedirs(RECORDING_PATH, exist_ok=True)
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URI = os.getenv('DATABASE_URI')
LOGGER = Logger(__name__, LOG_FILE)
MODEL = declarative_base()
ENGINE = create_engine(DATABASE_URI, echo=False)
SESSION_MAKER = sessionmaker(bind=ENGINE)
SESSION = SESSION_MAKER()
CONNECTIONS = {}

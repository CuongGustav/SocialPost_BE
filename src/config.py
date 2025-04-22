from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PSWD = os.getenv("DB_PSWD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

encoded_pswd = quote_plus(DB_PSWD)

DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pswd}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
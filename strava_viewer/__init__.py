import os

from dotenv import load_dotenv

__version__ = "0.1.0"

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

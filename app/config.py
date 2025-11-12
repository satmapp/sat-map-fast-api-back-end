import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
LNBITS_URL = os.getenv("LNBITS_URL")
LNBITS_ADMIN_KEY = os.getenv("LNBITS_ADMIN_KEY")
LNBITS_INVOICE_KEY = os.getenv("LNBITS_INVOICE_KEY")


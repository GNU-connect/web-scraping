import sentry_sdk
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
)
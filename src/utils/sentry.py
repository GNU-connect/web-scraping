import sentry_sdk
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
)
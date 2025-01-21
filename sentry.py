import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry(app):
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN', ''),  # You'll need to set this in Vercel env
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
    return app

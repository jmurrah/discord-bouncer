import logging
import os
import warnings

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from google.cloud import secretmanager

from .database import delete_expired_members

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning, module="google.cloud.firestore")


def load_secrets_into_env():
    logger.info("Loading secrets into environment.")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    secrets_manager = secretmanager.SecretManagerServiceClient()
    secrets = secrets_manager.list_secrets(request={"parent": f"projects/{project_id}"})

    for secret in secrets:
        secret_version = secrets_manager.access_secret_version(
            request={"name": f"{secret.name}/versions/latest"}
        )
        secret_value = secret_version.payload.data.decode("UTF-8")
        secret_name = secret.name.split("/")[-1]

        logger.info(f"Setting {secret_name} in environment!")
        os.environ[secret_name] = secret_value


def initialize_member_expiration_check():
    logging.info("Setting up member expiration check.")
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_members, "cron", hour=0)
    scheduler.start()


def setup_environment():
    logging.info("Setting up environment.")
    # load_secrets_into_env()
    load_dotenv(override=True)
    initialize_member_expiration_check()

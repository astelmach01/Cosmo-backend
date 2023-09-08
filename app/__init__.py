"""app package."""
import logging
import os

import botocore.session
from botocore.configloader import raw_config_parse

from app.settings import settings


def set_aws_credentials_and_region(
    access_key, secret_key, region_name, profile_name="default"
):
    """Set AWS credentials and region using botocore."""

    # Create a botocore session
    session = botocore.session.Session()

    # Load existing configuration if it exists
    credentials_file = os.path.expanduser("~/.aws/credentials")
    config_file = os.path.expanduser("~/.aws/config")

    if os.path.exists(credentials_file):
        existing_credentials = raw_config_parse(credentials_file)
    else:
        existing_credentials = {}

    if os.path.exists(config_file):
        existing_config = raw_config_parse(config_file)
    else:
        existing_config = {}

    # Set the credentials for the desired profile
    if profile_name not in existing_credentials:
        existing_credentials[profile_name] = {}
    existing_credentials[profile_name]["aws_access_key_id"] = access_key
    existing_credentials[profile_name]["aws_secret_access_key"] = secret_key

    # Set the region for the desired profile
    profile_config_key = (
        f"profile {profile_name}" if profile_name != "default" else "default"
    )
    if profile_config_key not in existing_config:
        existing_config[profile_config_key] = {}
    existing_config[profile_config_key]["region"] = region_name

    # Save the updated configurations
    session.full_config = existing_credentials
    session.set_config_variable("credentials_file", credentials_file)
    session.emit("session-initialized", session=session)
    session.emit("before-config-write", config=existing_credentials)

    session.full_config = existing_config
    session.set_config_variable("config_file", config_file)
    session.emit("session-initialized", session=session)
    session.emit("before-config-write", config=existing_config)

    logging.info(
        f"Credentials and region for profile '{profile_name}' \
        added to AWS configuration."
    )


if settings.ENVIRONMENT != "development":
    set_aws_credentials_and_region(
        settings.AWS_ACCESS_KEY,
        settings.AWS_SECRET_ACCESS_KEY,
        settings.AWS_REGION,
        profile_name="default",
    )

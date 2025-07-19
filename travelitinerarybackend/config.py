from typing import Optional

from pydantic_settings import BaseSettings


# load the .env file
class BaseConfig(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}
    ENV_STATE: Optional[str] = None


# define the global config variables
class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    SECRET_KEY: str
    ALGORITHM: str


class DevConfig(GlobalConfig):
    model_config = {"env_file": ".env", "env_prefix": "DEV_", "extra": "ignore"}
    GCP_PROJECT_ID : str
    GCP_REGION : str

class ProdConfig(GlobalConfig):
    model_config = {"env_file": ".env", "env_prefix": "PROD_", "extra": "ignore"}


class TestConfig(GlobalConfig):
    model_config = {"env_file": ".env.test", "env_prefix": "TEST_", "extra": "ignore"}
    GCP_PROJECT_ID: Optional[str] = None
    GCP_REGION: Optional[str] = None


def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
    }
    if env_state not in configs:
        raise ValueError(
            f"Invalid env_state: {env_state}. Must be one of {list(configs.keys())}"
        )
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)

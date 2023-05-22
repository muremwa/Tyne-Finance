import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class EnvVariables:
    debug: str
    secret_key: str
    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: str


def load_variables() -> EnvVariables:
    # Path to the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), 'tf.env')

    # Load variables from the .env file
    load_dotenv(dotenv_path)

    variables = EnvVariables(
        os.getenv('DEBUG'),
        os.getenv('SECRET_KEY'),
        os.getenv('DATABASE_NAME'),
        os.getenv('DATABASE_USER'),
        os.getenv('DATABASE_PASSWORD'),
        os.getenv('DATABASE_HOST'),
        os.getenv('DATABASE_PORT')
    )

    if [val for val in vars(variables).values() if not val]:
        raise EnvironmentError('Some variable are missing')

    return variables

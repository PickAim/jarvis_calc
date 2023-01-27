import json
import base64
from datetime import timedelta, datetime

ENCODED_DATA_KEY: str = 'to_encode'
EXPIRES_TIME_KEY: str = 'expires_in'
GRANT_TYPE_KEY: str = 'grant_type'


TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class Tokenizer:
    @staticmethod
    def create_access_token(to_encode: any, expires_delta: timedelta = None, grant_type: int = 1) -> bytes:
        if expires_delta:
            expires_in = datetime.now() + expires_delta
        else:
            expires_in = datetime.now() + timedelta(minutes=30)
        expires_in = expires_in.replace(microsecond=0)
        data: dict[str, any] = {
            ENCODED_DATA_KEY: to_encode,
            EXPIRES_TIME_KEY: str(expires_in),
            GRANT_TYPE_KEY: grant_type
        }
        return base64.b64encode(json.dumps(data).encode())

    @staticmethod
    def is_token_expired(token: bytes) -> bool:
        token_data: dict[str, any] = json.loads(base64.standard_b64decode(token))
        return datetime.now() > datetime.strptime(token_data[EXPIRES_TIME_KEY], TIME_FORMAT)

import uuid
from fastapi.security import OAuth2PasswordBearer


def generate_uuid():
    return str(uuid.uuid4())


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

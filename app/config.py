import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        # ejemplo local MySQL:
        "mysql+pymysql://root:tu_password@localhost/impulso_comercial?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esta_clave")

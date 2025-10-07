import os
import secrets
import string

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///impulso_comercial.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    def get_secret_key():
        secret = os.getenv("SECRET_KEY")
        if not secret or secret == "cambia_esta_clave":
            # Intentar cargar clave existente del archivo
            key_file = os.path.join(os.path.dirname(__file__), '..', '.secret_key')
            if os.path.exists(key_file):
                try:
                    with open(key_file, 'r') as f:
                        secret = f.read().strip()
                        if secret and len(secret) >= 32:
                            print("[OK] SECRET_KEY cargada desde archivo")
                            return secret
                except:
                    pass
            
            # Generar nueva clave y guardarla
            new_secret = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(64))
            try:
                with open(key_file, 'w') as f:
                    f.write(new_secret)
                print("[OK] SECRET_KEY generada y guardada en .secret_key")
            except:
                print("[WARNING] No se pudo guardar SECRET_KEY. Se regenerará en cada reinicio.")
            return new_secret
        return secret
    
    SECRET_KEY = get_secret_key()
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_CV_EXT = {".pdf", ".doc", ".docx"}
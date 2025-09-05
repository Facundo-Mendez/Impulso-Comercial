from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Configurar logger para seguridad
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

# Handler para archivo de logs de seguridad
security_handler = logging.FileHandler('logs/security.log')
security_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
security_logger.addHandler(security_handler)

class SecurityMonitor:
    """Monitor de seguridad para detectar patrones sospechosos"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.suspicious_ips = set()
        
    def log_failed_login(self, ip_address, email=None):
        """Registrar intento de login fallido"""
        now = datetime.utcnow()
        self.failed_attempts[ip_address].append(now)
        
        # Limpiar intentos antiguos (más de 1 hora)
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address] 
            if attempt > cutoff
        ]
        
        # Marcar IP como sospechosa si tiene más de 10 intentos fallidos en 1 hora
        if len(self.failed_attempts[ip_address]) > 10:
            self.suspicious_ips.add(ip_address)
            security_logger.warning(
                f"IP sospechosa detectada: {ip_address} - {len(self.failed_attempts[ip_address])} intentos fallidos"
            )
        
        # Log del intento
        security_logger.warning(
            f"Login fallido desde {ip_address}" + (f" para email {email}" if email else "")
        )
    
    def log_successful_login(self, ip_address, user_id, email):
        """Registrar login exitoso"""
        # Limpiar intentos fallidos para esta IP
        if ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
        
        # Remover de IPs sospechosas
        self.suspicious_ips.discard(ip_address)
        
        security_logger.info(f"Login exitoso: usuario {user_id} ({email}) desde {ip_address}")
    
    def is_suspicious_ip(self, ip_address):
        """Verificar si una IP es sospechosa"""
        return ip_address in self.suspicious_ips
    
    def get_failed_attempts_count(self, ip_address):
        """Obtener número de intentos fallidos para una IP"""
        return len(self.failed_attempts.get(ip_address, []))

# Instancia global del monitor
security_monitor = SecurityMonitor()

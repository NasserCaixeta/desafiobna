from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB # Importa o tipo JSONB!
import datetime

class ScrapedData(db.Model):
    """
    Modelo da tabela para armazenar o cache do scraping.
    """
    __tablename__ = 'scraped_data_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # URL única e indexada para buscas rápidas
    url = db.Column(db.String(2048), unique=True, nullable=False, index=True) 
    
    # A "coluna mágica" para armazenar nosso JSON
    data = db.Column(JSONB, nullable=False)
    
    # Data de quando o scrape foi feito
    scraped_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ScrapedData {self.url}>'

class User(db.Model):
    """
    Modelo da tabela para armazenar os usuários da aplicação.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Usamos email como login. unique=True garante que não haja emails repetidos.
    email = db.Column(db.String(255), unique=True, nullable=False, index=True) 

    # Coluna para armazenar a senha Criptografada (hash)
    password_hash = db.Column(db.String(255), nullable=False)

    # Bônus: Coluna de Admin
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
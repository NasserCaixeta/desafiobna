import os
import datetime
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "uma-chave-secreta-forte")
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # POR ISTO:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=2)
    
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuração de Desenvolvimento"""
    DEBUG = True

class TestingConfig(Config):
    """Configuração de Testes"""
    TESTING = True
    MONGO_URI = os.getenv("MONGO_TEST_URI", "mongodb://localhost:27017/sales_scraper_test_db")

class ProductionConfig(Config):
    """Configuração de Produção"""
    SECRET_KEY = os.getenv("SECRET_KEY") 
    MONGO_URI = os.getenv("MONGO_URI") 

# Dicionário para facilitar a seleção da config
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig}
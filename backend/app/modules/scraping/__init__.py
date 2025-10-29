from flask import Blueprint

# Define o Blueprint com o prefixo da API
scraping_bp = Blueprint(
    'scraping', 
    __name__, 
    url_prefix='/api/v1/scraping'
)

# Importa as rotas (que irão usar este 'scraping_bp')
from . import routes
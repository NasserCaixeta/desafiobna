from flask import Blueprint, request, jsonify
from . import scraping_bp 
from .services import get_scraped_data_service 
from flask_jwt_extended import jwt_required 

# /api/v1/scraping/scrape
@scraping_bp.route('/scrape', methods=['POST'])
@jwt_required() # SÓ utilizadores logados podem fazer scrape
def scrape_website():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400

    try:
        
        scraped_data = get_scraped_data_service(url)
        return jsonify(scraped_data), 200
    
    except Exception as e:
        # Captura erros (ex: Timeout, API Key inválida, etc.)
        print(f"ERRO GERAL na Rota de Scrape: {e}")
        return jsonify({"error": f"Falha no scraping: {str(e)}"}), 500
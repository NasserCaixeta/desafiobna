import os
from flask import Flask


# Importa as extensões que vamos inicializar
from .extensions import db, cors, bcrypt, jwt
# Importa os Modelos (para o SQLAlchemy saber deles)
from .models import User, ScrapedData


def create_app(config_name="default"):
    """
    Factory Function (Fábrica de Aplicação)
    """
    
    # 1. Cria a instância principal do Flask
    app = Flask(__name__)
    
    # Importa as classes de config.py e constrói o dicionário manualmente.
    
    try:
        from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
    except ImportError:
        # Fallback se o usuário tiver apenas a classe 'Config'
        try:
            from config import Config
            # Se só houver 'Config', usaremos ela para tudo
            DevelopmentConfig = Config
            ProductionConfig = Config
            TestingConfig = Config
        except ImportError as e:
            raise ImportError(
                f"Não foi possível importar as classes de config.py "
                f"(Config, DevelopmentConfig, etc). "
                f"Verifique seu arquivo config.py. Erro original: {e}"
            )

    # Cria o dicionário de mapeamento manualmente
    config_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig  # Define 'default' como 'development'
    }
    
    # 2. Carrega a configuração (Development, Production, etc.)
    #
    # 'config_dict.get(...)' retorna a CLASSE (ex: DevelopmentConfig)
    config_class_object = config_dict.get(config_name, config_dict["default"])
    
    # Agora carregamos as configurações A PARTIR DO OBJETO DE CLASSE
    app.config.from_object(config_class_object)
    
    # 3. Inicializa as extensões com a app
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Permite CORS em /api/
    bcrypt.init_app(app)
    jwt.init_app(app)
    # Importa os Blueprints (módulos da aplicação) AQUI
    # (Dentro da função, depois que o 'db' foi inicializado)
    from .modules.admin import admin_bp
    from .modules.auth import auth_bp
    from .modules.scraping import scraping_bp 

    # 4. Registra os Blueprints (rotas)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(scraping_bp)

    # Bônus: Cria tabelas se não existirem
    with app.app_context():
        # db.drop_all() # Cuidado: Usar só em dev para limpar
        db.create_all()

    return app
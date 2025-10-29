from flask import Blueprint

# O nome da string DEVE ser 'admin_bp'
admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/api/v1/admin'  
)

from . import routes
import os
import datetime
import re
import json
from bs4 import BeautifulSoup
from sqlalchemy import exc
from urllib.parse import urlparse, urljoin

# --- Importações do Selenium ---\
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# --- Importar o "Cérebro" (Google AI) ---\
import google.generativeai as genai

# Configurar o caminho do driver
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
DRIVER_NAME = "chromedriver.exe" if os.name == 'nt' else "chromedriver"
DRIVER_PATH = os.path.join(project_root, DRIVER_NAME)



# ==============================================================================
# 1. FUNÇÕES DO SELENIUM 
# ==============================================================================

def _init_selenium_driver():
    """
    Inicializa um driver do Chrome (Selenium) otimizado e headless.
    """
    service = Service(executable_path=DRIVER_PATH)
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(20) # Timeout de 20 segundos
    except WebDriverException as e:
        print(f"ERRO CRÍTICO: Não foi possível encontrar o '{DRIVER_NAME}'.")
        print("Certifique-se de que o 'chromedriver' (ou 'chromedriver.exe') está na pasta raiz do projeto backend.")
        raise Exception(f"WebDriver não encontrado: {e}")
    
    return driver

def scrape_home_page_dossier(driver, url):
    """
    (V7.0) Acessa a página principal e extrai o "dossiê" (título, H1, metas, links, etc.)
    Retorna o (HTML, Dossiê JSON, Texto para AI)
    """
    print(f"Selenium acessando (página principal): {url}...")
    driver.get(url)
    
    # Espera até que o <body> esteja presente
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("Página principal carregada, analisando...")
    
    # 1. Extração de Metadados
    titulo = soup.title.string if soup.title else ''
    
    # Pega o H1 (usa .get_text para limpar tags internas)
    h1_tag = soup.find('h1')
    h1_principal = h1_tag.get_text(strip=True) if h1_tag else ''

    # Pega a meta description
    descricao_meta_tag = soup.find('meta', attrs={'name': 'description'})
    descricao_meta = descricao_meta_tag['content'] if descricao_meta_tag and 'content' in descricao_meta_tag.attrs else ''

    # Pega meta keywords
    meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    keywords_raw = meta_keywords_tag['content'] if meta_keywords_tag and 'content' in meta_keywords_tag.attrs else ''
    meta_keywords = [k.strip() for k in keywords_raw.split(',')] if keywords_raw else []

    # 2. Extração de Contatos (Email e Redes Sociais)
    emails_encontrados = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content))
    
    links_sociais = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if any(rede in href for rede in ['linkedin.com', 'facebook.com', 'instagram.com', 'twitter.com', 'wa.me', 'whatsapp.com']):
            links_sociais.add(href)

    # 3. Extração de CTAs (Call-to-Action)
    ctas_encontrados = set()
    cta_keywords = ['contato', 'fale conosco', 'orçamento', 'saiba mais', 'agende', 'demonstração', 'teste grátis']
    
    # Procura em <a>
    for a_tag in soup.find_all('a'):
        text = a_tag.get_text(strip=True).lower()
        if any(keyword in text for keyword in cta_keywords):
            ctas_encontrados.add(a_tag.get_text(strip=True))
            
    # Procura em <button>
    for btn_tag in soup.find_all('button'):
        text = btn_tag.get_text(strip=True).lower()
        if any(keyword in text for keyword in cta_keywords):
            ctas_encontrados.add(btn_tag.get_text(strip=True))

    # 4. Extração de Texto (para Contagem e para a AI)
    texto_bruto = soup.get_text(separator=' ', strip=True)
    contagem_palavras_home = len(texto_bruto.split())

    # Compila o Dossiê
    dossie_json = {
        "url": url,
        "titulo": titulo,
        "h1_principal": h1_principal,
        "descricao_meta": descricao_meta,
        "meta_keywords": list(meta_keywords),
        "emails_encontrados": list(emails_encontrados),
        "links_sociais": list(links_sociais),
        "ctas_encontrados": list(ctas_encontrados),
        "contagem_palavras_home": contagem_palavras_home
        # As chaves 'analise_ia' e 'tecnologias' serão adicionadas depois
    }
    
    return html_content, dossie_json, texto_bruto


def scrape_sub_page_analysis(driver, base_url, soup_home):
    """
    (V7.0) Acessa até 5 sub-páginas (ex: /sobre) e extrai
    o "mapa de conteúdo" (H2, H3) e o texto principal.
    Retorna (Lista de Dossiês de Sub-página, Texto da Sub-página para AI)
    """
    
    # 1. Encontrar links internos relevantes (Sobre, Serviços, Contato, etc.)
    # Usamos regex para encontrar links que PARECEM ser de conteúdo
    links_internos = set()
    palavras_chave_links = r'(sobre|quem-somos|servicos|produtos|contato|empresa|institucional|solucoes)'
    
    for a_tag in soup_home.find_all('a', href=True):
        href = a_tag['href']
        # Garante que é um link interno e relevante
        if href.startswith('/') or href.startswith(base_url):
            if re.search(palavras_chave_links, href, re.IGNORECASE):
                full_url = urljoin(base_url, href) # Constrói URL completa
                links_internos.add(full_url)
    
    # Limita a 5 links para não sobrecarregar
    links_para_visitar = list(links_internos)[:5]
    print(f"Links de conteúdo encontrados para análise: {links_para_visitar}")

    lista_dossies_subpaginas = []
    texto_total_subpaginas = ""

    # 2. Visitar cada link
    for link in links_para_visitar:
        try:
            print(f"Acessando sub-página para análise profunda: {link}...")
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            soup_subpage = BeautifulSoup(driver.page_source, 'html.parser')

            titulo_pagina = soup_subpage.title.string if soup_subpage.title else ''

            # 3. Extrair Mapa de Conteúdo (H2 e H3)
            mapa_conteudo = []
            for heading in soup_subpage.find_all(['h2', 'h3']):
                mapa_conteudo.append(f"{heading.name.upper()}: {heading.get_text(strip=True)}")
            
            # 4. Extrair Texto
            texto_subpagina = soup_subpage.get_text(separator=' ', strip=True)
            texto_total_subpaginas += f"\n\n--- CONTEÚDO DA PÁGINA: {link} ---\n{texto_subpagina}"

            # 5. Compilar Dossiê
            lista_dossies_subpaginas.append({
                "url_visitada": link,
                "titulo_da_pagina": titulo_pagina,
                "mapa_de_conteudo_headings": mapa_conteudo
            })

        except TimeoutException:
            print(f"Timeout ao acessar sub-página: {link}. Ignorando.")
        except Exception as e:
            print(f"Erro ao analisar sub-página {link}: {e}. Ignorando.")
            
    return lista_dossies_subpaginas, texto_total_subpaginas


# ==============================================================================
# 2. FUNÇÕES DE ANÁLISE (REGEX e IA)
# ==============================================================================

def _detect_technology_stack(html_content):
    """
    (V8.1) Usa Regex simples para tentar adivinhar tecnologias no HTML.
    """
    tech_stack = []
    
    # Dicionário de Regex
    tech_patterns = {
        'React': r'react-dom|react\.js|react\.min\.js',
        'Vue.js': r'vue\.js|vue\.min\.js',
        'Angular': r'angular\.js|angular\.min\.js',
        'jQuery': r'jquery\.js|jquery\.min\.js',
        'WordPress': r'wp-content|wp-includes',
        'Shopify': r'cdn\.shopify\.com',
        'VTEX': r'vteximg\.com\.br|vtexassets\.com',
        'Nuvemshop': r'cdn\.nuvemshop\.com\.br',
        'Wix': r'wix\.com|static\.parastorage\.com',
        'Google Analytics': r'google-analytics\.com/analytics\.js|gtag\(\'config\', \'UA-',
        'Google Tag Manager': r'googletagmanager\.com/gtm\.js',
        'Hotjar': r'static\.hotjar\.com',
        'RD Station': r'tools\.rdstation\.com\.br',
    }

    for tech, pattern in tech_patterns.items():
        if re.search(pattern, html_content, re.IGNORECASE):
            tech_stack.append(tech)
            
    if not tech_stack:
        return ["Nenhuma tecnologia específica detectada"]
        
    return tech_stack

# --- (PROMPT ATUALIZADO V8.5) ---
# Este prompt é mais simples e focado no "propósito geral", como pedido.
PROMPT_GERAL_V8_5 = """
Contexto: Você é um assistente de análise de conteúdo. Sua tarefa é ler o texto de um site e resumi-lo de forma objetiva.
Retorne APENAS um objeto JSON válido.

O seu JSON de saída DEVE conter EXATAMENTE as seguintes chaves:
{
  "general_summary": "Um resumo geral (2-3 frases) sobre o que é esta página e qual seu propósito principal.",
  "main_subject": "Qual é o assunto principal ou o produto/serviço central oferecido?",
  "target_audience": "Para quem este site se destina? (ex: 'Desenvolvedores', 'Empresas de Varejo', 'Consumidores Finais')."
}
"""

# --- (FUNÇÃO ATUALIZADA V8.5) ---
def _analyze_text_with_ai(full_text_content):
    """
    (V8.5) Tenta analisar o texto com o Gemini.
    Usa o 'models/gemini-pro-latest' e o novo prompt V8.5 (foco geral).
    É "safe-fail" - se falhar, retorna {} e não quebra o request (Erro 500).
    """
    print("Iniciando chamada à API do Gemini (V8.5) para análise geral...")
    
    try:
        # --- Configurar a API DENTRO da função ---
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        
        # 1. Verifica se a chave existe
        if not GOOGLE_API_KEY:
            print("AVISO: Análise de AI ignorada (GOOGLE_API_KEY não encontrada no .env).")
            return {} # Retorna um JSON vazio
        
        # 2. Configura a API 
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # --- Usando o modelo que a sua chave suporta ---
        model = genai.GenerativeModel('models/gemini-pro-latest')

        # 3. Define as regras de geração
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0.3, 
            response_mime_type="application/json", 
        )

        # 4. Combina o prompt com o conteúdo
        
        prompt_combinado = f"{PROMPT_GERAL_V8_5}\n\nTexto do Site:\n{full_text_content}"
        
        # 5. Faz a chamada à API
        response = model.generate_content(
            prompt_combinado,
            generation_config=generation_config
        )

        # 6. Extrai o JSON da resposta
        ai_json = json.loads(response.text)
        print("Sucesso: Análise de IA do Gemini (V8.5) recebida.")
        return ai_json

    except Exception as e:
        # Captura QUALQUER erro (Chave Inválida, API offline, Modelo não encontrado)
        print(f"!!! ERRO CRÍTICO AO CHAMAR O GEMINI AI !!!: {e}")
        print("A análise de IA será retornada vazia.")
        # Retorna um JSON vazio para não quebrar o frontend
        return {}


# ==============================================================================
# 3. FUNÇÃO PRINCIPAL DE SERVIÇO (O "CÉREBRO")
# ==============================================================================

def get_scraped_data_service(url):
    """
    (V8.1) Orquestra todo o processo de scraping e análise.
    1. Verifica Cache (DB)
    2. Se não tem cache, usa Selenium (Aranha)
    3. Faz análise de Tech Stack (Regex)
    4. Faz análise de Vendas (Gemini AI)
    5. Salva no Cache
    6. Retorna o JSON completo
    """
    
    
    
    from app.extensions import db
    from app.models import ScrapedData
   
    
    # Limpa a URL (ex: remove / no final)
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip('/')
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # 1. VERIFICAR CACHE
    try:
        cache_duration_days = 1
        cache_cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=cache_duration_days)
        
        cached_data = ScrapedData.query.filter(
            ScrapedData.url == url,
            ScrapedData.scraped_at > cache_cutoff
        ).first()

        if cached_data:
            print(f"CACHE HIT: Retornando dados do Postgres para {url}")
            return cached_data.data # Retorna o JSONB salvo

    except exc.SQLAlchemyError as e:
        # Se o DB estiver offline, não quebra, apenas ignora o cache
        print(f"AVISO: Erro ao consultar o cache no DB: {e}. Prosseguindo com scrape.")
    
    print(f"CACHE MISS: Fazendo novo scrape (com Selenium) para {url}")
    
    # 2. INICIAR ARANHA (SELENIUM)
    driver = None
    try:
        driver = _init_selenium_driver()

        # 3. FAZER SCRAPE DA HOME + SUB-PÁGINAS
        
        # 3.1. Home Page
        html_home, dossie_home_json, texto_home = scrape_home_page_dossier(driver, url)
        
        # 3.2. Sub-Páginas
        soup_home = BeautifulSoup(html_home, 'html.parser')
        lista_dossies_subpaginas, texto_subpaginas = scrape_sub_page_analysis(driver, base_url, soup_home)

    except TimeoutException:
        raise Exception(f"Erro de Timeout: A página {url} demorou muito para carregar.")
    except WebDriverException as e:
        raise Exception(f"Erro do WebDriver (verifique o chromedriver): {e}")
    except Exception as e:
        raise Exception(f"Erro durante o scrape do Selenium: {e}")
    finally:
        if driver:
            driver.quit() # Fecha o navegador

    # 4. FAZER ANÁLISES (REGEX e IA)
    
    # 4.1. Análise de Tech Stack (Regex)
    tech_stack_analysis = _detect_technology_stack(html_home)
    
    # 4.2. Análise de Vendas (Gemini AI)
    # Junta todo o texto (Home + Sub-páginas)
    texto_total_para_ia = texto_home + texto_subpaginas
    
    # Chama a nossa nova função "safe-fail" (V8.5)
    ai_analysis_json = _analyze_text_with_ai(texto_total_para_ia)

    # 5. COMPILAR O JSON DE RESULTADO FINAL
    try:
        # Adiciona as análises ao dossiê principal
        dossie_home_json["analise_ia"] = ai_analysis_json
        dossie_home_json["tecnologias_detetadas"] = tech_stack_analysis

        # Monta o objeto final
        result_json_data = {
            "dossie_pagina_principal": dossie_home_json,
            "analise_profunda_subpaginas": lista_dossies_subpaginas
        }
        
        # 6. Salvar no cache (DB)
        current_time = datetime.datetime.utcnow()
        try:
            entry_to_update = ScrapedData.query.filter_by(url=url).first()
            if entry_to_update:
                entry_to_update.data = result_json_data
                entry_to_update.scraped_at = current_time
                print(f"CACHE UPDATE: Atualizando dados no Postgres para {url}")
            else:
                new_entry = ScrapedData(url=url, data=result_json_data, scraped_at=current_time)
                db.session.add(new_entry)
                print(f"CACHE SET: Salvando novos dados no Postgres para {url}")
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            # Não quebra o request, apenas avisa do erro de cache
            print(f"AVISO: Não foi possível salvar o scrape no DB: {e}")

        # 7. Retornar o JSON
        return result_json_data

    except Exception as e:
        raise Exception(f"Erro ao compilar o JSON final ou salvar no cache: {e}")
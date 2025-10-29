import React from 'react';
import './ScrapeResult.css'; // Importa os novos estilos

// Helper para os "Crachás" (Tags)
const renderTags = (items, className, title) => {
  if (!items || items.length === 0) return null;
  return (
    <div className="result-tags-container">
      <h4 className="sub-heading">{title}</h4>
      {items.map((item, index) => (
        <span key={index} className={`result-tag ${className}`}>
          {item}
        </span>
      ))}
    </div>
  );
};

// Helper para as Listas de Contacto
const renderLinkList = (items, title, isMail = false) => {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h4 className="sub-heading">{title}</h4>
      <ul className="result-contacts-list">
        {items.map((item, index) => (
          <li key={index}>
            <a href={isMail ? `mailto:${item}` : item} target="_blank" rel="noopener noreferrer">
              {item}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

// --- Helper para a Análise de IA (V8.5) ---
const AiAnalysisSection = ({ analysis }) => {
  // Se a 'analise_ia' não existir ou vier vazia
  if (!analysis || Object.keys(analysis).length === 0) {
    return (
      <div className="ai-analysis-container">
        <h3>Análise (IA)</h3>
        <p className="no-results">
          A análise de IA não foi executada.
          (Verifique se a API Key do Google está configurada corretamente no .env do backend).
        </p>
      </div>
    );
  }

  
  const {
    general_summary,
    main_subject,
    target_audience
  } = analysis;

  return (
    <div className="ai-analysis-container">
      <h3>Análise (IA)</h3>
      
      <dl className="ai-analysis-list">
        
        <dt>Resumo Geral (Propósito):</dt>
        <dd>{general_summary || 'N/A'}</dd>

        <dt>Assunto Principal (Produto/Serviço):</dt>
        <dd>{main_subject || 'N/A'}</dd>

        <dt>Público-Alvo:</dt>
        <dd>{target_audience || 'N/A'}</dd>

      </dl>
    </div>
  );
};
// --- FIM DO HELPER ---


const ScrapeResult = ({ results }) => {
  // Desestrutura os dados
  const {
    dossie_pagina_principal,
    analise_profunda_subpaginas // (Usado para a contagem de 'Páginas')
  } = results;

  if (!dossie_pagina_principal) {
    return <p>Ocorreu um erro ao processar os resultados.</p>;
  }

  // 1. Dossiê da Página Principal
  const {
    url,
    titulo,
    h1_principal,
    descricao_meta,
    meta_keywords,
    emails_encontrados,
    links_sociais,
    ctas_encontrados,
    contagem_palavras_home,
    analise_ia, 
    tecnologias_detetadas
  } = dossie_pagina_principal;

  // Limpa a URL para exibição
  const cleanUrl = url.replace(/^(https?:\/\/)/, '').replace(/\/$/, '');
  
  // Contagens para o box de análise
  const techCount = tecnologias_detetadas ? tecnologias_detetadas.length : 0;
  const pageCount = analise_profunda_subpaginas ? analise_profunda_subpaginas.length : 0;


  return (
    <div className="result-wrapper">
      
      
      <h2 className="result-main-title">
        <a href={url} target="_blank" rel="noopener noreferrer">
          {cleanUrl}
        </a>
      </h2>

      {/* --- 1. Quadro de Análise --- */}
      <div className="analysis-box">
        <div className="analysis-item">
          <h4>Palavras (Home)</h4>
          <p>{contagem_palavras_home}</p>
        </div>
        <div className="analysis-item">
          <h4>Tecnologias</h4>
          <p>{techCount}</p>
        </div>
      </div>

      {/* --- 2. SECÇÃO DE IA  --- */}
      <AiAnalysisSection analysis={analise_ia} />

      {/* --- 3. Dossiê da Home Page --- */}
      <div className="result-dossie">
        <h3>Dossiê (Página Principal)</h3>
        {/* O link principal foi movido para o topo (V8.7) */}
        
        <h4 className="sub-heading">Título (Tag &lt;title&gt;):</h4>
        <p>{titulo || '(Nenhum)'}</p>

        <h4 className="sub-heading">Descrição (Meta Description):</h4>
        <p>{descricao_meta || '(Nenhuma meta description encontrada)'}</p>

        {renderTags(tecnologias_detetadas, "keyword", "Tecnologias Detectadas")}
      </div>

      {/* --- 4. Contactos e Links --- */}
      <div className="result-contacts">
        <h3>Contatos & Links</h3>
        <div className="contacts-grid">
          {renderLinkList(links_sociais, "Links Sociais (Redes)")}
          {renderLinkList(emails_encontrados, "Emails Encontrados", true)}
        </div>
        
        {renderTags(meta_keywords, "keyword", "Meta Keywords")}
        {renderTags(ctas_encontrados, "cta", "CTAs (Call-to-Action)")}
      </div>

    </div>
  );
};

export default ScrapeResult;
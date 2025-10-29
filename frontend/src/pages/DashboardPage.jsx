import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { IoSend } from 'react-icons/io5';
import ScrapeResult from '../components/ScrapeResult'; // <-- 1. IMPORTAR O NOVO COMPONENTE

const DashboardPage = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const [chatHistory, setChatHistory] = useState([
        { sender: 'bot', content: 'Olá! Por favor, insira uma URL de um site corporativo para eu analisar (ex: https://vtex.com/br-pt/).' }
    ]);

    const chatWindowRef = useRef(null);

    useEffect(() => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [chatHistory]);


    const handleScrape = async (e) => {
        e.preventDefault();
        if (loading || !url) return;

        setLoading(true);
        setError('');

        setChatHistory(prev => [
            ...prev,
            { sender: 'user', content: `Analisar: ${url}` }
        ]);
        
        const urlToScrape = url; 
        setUrl(''); 

        try {
            const response = await api.post('/scraping/scrape', {
                url: urlToScrape
            });
            
            setChatHistory(prev => [
                ...prev,
                { sender: 'bot', content: response.data }
            ]);

        } catch (err) {
            let errorMessage = "Erro desconhecido.";
            if (err.response && err.response.data && err.response.data.error) {
                errorMessage = err.response.data.error;
            } else if (err.message) {
                errorMessage = err.message;
            }
            
            setChatHistory(prev => [
                ...prev,
                { sender: 'bot', content: `Erro ao analisar ${urlToScrape}: ${errorMessage}`, isError: true }
            ]);
            setError(errorMessage); 
        } finally {
            setLoading(false);
        }
    };

    
    const renderBotMessage = (message) => {
        if (message.isError) {
            return <p style={{color: 'var(--color-danger)'}}>{message.content}</p>;
        }
        
        if (typeof message.content === 'object') {
            
            return <ScrapeResult results={message.content} />;
        }
        return <p>{message.content}</p>;
    };

    return (
        <div className="chat-dashboard">
            
            {/* 1. A Janela do Chat (com histórico) */}
            <div className="chat-window" ref={chatWindowRef}>
                {chatHistory.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.sender}`}>
                        {msg.sender === 'user' ? (
                            <p>{msg.content}</p>
                        ) : (
                            renderBotMessage(msg) 
                        )}
                    </div>
                ))}
                {/* Mostra "Bot está a digitar..." */}
                {loading && (
                    <div className="chat-message bot">
                        <p>Analisando o site... pode demorar 20-30 segundos...</p>
                    </div>
                )}
            </div>

            {/* 2. A Barra de Input (Estilo Gemini) */}
            <form onSubmit={handleScrape} className="gemini-input-bar">
                <input
                    type="url"
                    placeholder="Insira uma URL para prospectar..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="gemini-input"
                    required
                    disabled={loading}
                />
                <button type="submit" className="gemini-send-button" disabled={loading}>
                    <IoSend /> 
                </button>
            </form>
        </div>
    );
};

export default DashboardPage;
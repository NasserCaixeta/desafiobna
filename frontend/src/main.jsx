import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import { BrowserRouter } from 'react-router-dom';

// CSS Global Simples (para limpar o padrão do navegador)
import './index.css'; 

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter> {/* O Roteador */}
      <AuthProvider> {/* O Cérebro */}
        <App /> {/* O nosso App */}
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
import React, { createContext, useState, useContext, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api'; // <-- 1. PRECISAMOS DE IMPORTAR O 'api'

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    // Vamos usar 'token' como a chave, para ser consistente
    const [token, setToken] = useState(localStorage.getItem('token')); 
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true); // Estado de carregamento

    // useEffect: Roda UMA VEZ quando a app carrega
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            try {
                const decodedUser = jwtDecode(storedToken);
                
                if (decodedUser.exp * 1000 > Date.now()) {
                    // --- CORREÇÃO 1: CONFIGURAR O API NO LOAD ---
                    // Se o token for válido, diz ao Axios para usá-lo
                    api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
                    setToken(storedToken);
                    setUser(decodedUser);
                } else {
                    localStorage.removeItem('token'); // Token expirado
                }
            } catch (e) {
                localStorage.removeItem('token'); // Token inválido
            }
        }
        setIsLoading(false); // Termina o carregamento
    }, []); // Array vazio = roda 1 vez no início

    const login = (newToken) => {
        try {
            localStorage.setItem('token', newToken); // Salva o novo token
            const decodedUser = jwtDecode(newToken);
            
            // --- CORREÇÃO 2: CONFIGURAR O API NO LOGIN ---
            // Diz ao Axios para usar este NOVO token a partir de agora
            api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
            
            setToken(newToken);
            setUser(decodedUser);
        } catch (e) {
            console.error("Erro ao decodificar token:", e);
            logout();
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        
        // --- CORREÇÃO 3: LIMPAR O API NO LOGOUT ---
        // Diz ao Axios para parar de usar o token
        delete api.defaults.headers.common['Authorization'];
        
        setToken(null);
        setUser(null);
    };

    const isAuthenticated = !!token;
    const isAdmin = user?.is_admin || false;

    // Não mostra a app até que a verificação inicial esteja completa
    if (isLoading) {
        return <div>A carregar autenticação...</div>;
    }

    return (
        <AuthContext.Provider value={{ token, user, isAuthenticated, isAdmin, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Link } from 'react-router-dom'; // <-- 1. IMPORTAR O LINK

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); 

        try {
            const response = await api.post('/auth/login', { email, password });
            login(response.data.access_token);
        } catch (err) {
            if (err.response && err.response.data) {
                setError(err.response.data.error || "Erro ao fazer login.");
            } else {
                setError("Servidor não disponível. (Verifique se o backend está rodando!)");
            }
        }
    };

    return (
        <div className="form-container">
            <form onSubmit={handleSubmit}>
                <h2>Login</h2>
                <div className="input-group">
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="input-field"
                        required
                    />
                </div>
                <div className="input-group">
                    <input
                        type="password"
                        placeholder="Senha"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field"
                        required
                    />
                </div>
                <button type="submit" className="primary-button">Entrar</button>
                {error && <p className="error-message">{error}</p>}

                {/* --- 2. ADICIONAR O LINK DE REGISTO --- */}
                <div style={{marginTop: '20px', textAlign: 'center'}}>
                    <Link to="/register" style={{color: 'var(--color-text-secondary)'}}>
                        Primeiro acesso? Crie a conta Admin aqui.
                    </Link>
                </div>
                
            </form>
        </div>
    );
};

export default LoginPage;
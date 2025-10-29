import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const RegisterPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(''); 
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            // 1. Tenta fazer o POST para a API de registo do Flask
            const response = await api.post('/auth/register', {
                email: email,
                password: password
            });

            
            setSuccess(response.data.message + " Você será redirecionado para o login em 3 segundos.");
            
            // 3. Redireciona para o login (para que ele possa usar as novas credenciais)
            setTimeout(() => {
                navigate('/login');
            }, 3000);

        } catch (err) {
            // 4. FALHA! (Provavelmente um 403 Forbidden, "Registro público desativado")
            if (err.response && err.response.data) {
                setError(err.response.data.error || "Erro ao registrar.");
            } else {
                setError("Servidor não disponível. (Verifique se o backend está rodando!)");
            }
        }
    };

    return (
        
        <div className="form-container"> 
            <form onSubmit={handleSubmit}>
                <h2>Criar Conta de Administrador</h2>
                <p style={{color: 'var(--color-text-secondary)', fontSize: '0.9rem', marginTop: '-15px', marginBottom: '20px', textAlign: 'center'}}>
                    (Esta tela só funciona se for o primeiro utilizador do sistema)
                </p>
                
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
                
                <button type="submit" className="primary-button" disabled={!!success}>
                    {success ? 'Registado!' : 'Criar Conta'}
                </button>
                
                {error && <p className="error-message">{error}</p>}
                {success && <p style={{color: 'var(--color-success)', marginTop: '15px'}}>{success}</p>}

                <div style={{marginTop: '20px', textAlign: 'center'}}>
                    <Link to="/login" style={{color: 'var(--color-text-secondary)'}}>
                        Já tem uma conta? Faça Login
                    </Link>
                </div>
            </form>
        </div>
    );
};

export default RegisterPage;
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const AdminPage = () => {
    // Estados para utilizadores
    const [users, setUsers] = useState([]);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

   
    const [cacheMessage, setCacheMessage] = useState('');
    const [cacheError, setCacheError] = useState('');
    const [isClearingCache, setIsClearingCache] = useState(false);
    

    // Função para carregar os utilizadores
    const fetchUsers = async () => {
        try {
            const response = await api.get('/admin/users');
            setUsers(response.data);
        } catch (err) {
            
            console.error("Erro ao buscar usuários:", err);
            setError('Não foi possível carregar utilizadores.');
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleCreateUser = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        try {
            const response = await api.post('/admin/users', { email, password, is_admin: isAdmin });
            setMessage(response.data.message);
            fetchUsers();
            setEmail('');
            setPassword('');
            setIsAdmin(false);
        } catch (err) {
            setError(err.response?.data?.error || 'Erro ao criar utilizador.');
        }
    };

    const handleDeleteUser = async (userId) => {
        if (window.confirm('Tem certeza que deseja deletar este utilizador?')) {
            try {
                await api.delete(`/admin/users/${userId}`);
                setMessage('Utilizador deletado com sucesso.');
                fetchUsers();
            } catch (err) {
                setError(err.response?.data?.error || 'Erro ao deletar utilizador.');
            }
        }
    };

    
    const handleClearCache = async () => {
        if (!window.confirm('Tem certeza que deseja apagar TODO o cache de scraping? Todos os sites terão de ser re-analisados.')) {
            return;
        }
        setIsClearingCache(true);
        setCacheMessage('');
        setCacheError('');
        try {
            const response = await api.post('/admin/clear-cache'); // Chama a nova rota
            setCacheMessage(response.data.message);
        } catch (err) {
            setCacheError(err.response?.data?.error || 'Erro ao comunicar com o servidor.');
        } finally {
            setIsClearingCache(false);
        }
    };
    

    return (
        <div className="admin-page-container">
            <h1>Painel de Administração</h1>

            
            <div className="admin-widget">
                <h3>Criar Novo Utilizador</h3>
                <form onSubmit={handleCreateUser} className="admin-form">
                    {error && <p className="error-message">{error}</p>}
                    {message && <p className="success-message">{message}</p>}
                    <div className="input-group">
                        <input type="email" placeholder="Email do novo utilizador" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" required />
                    </div>
                    <div className="input-group">
                        <input type="password" placeholder="Senha temporária" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" required />
                    </div>
                    <label className="checkbox-label">
                        <input type="checkbox" checked={isAdmin} onChange={(e) => setIsAdmin(e.target.checked)} />
                        Tornar este utilizador um Admin?
                    </label>
                    <button type="submit" className="primary-button">
                        Criar Utilizador
                    </button>
                </form>
            </div>

           
            <div className="admin-widget">
                <h3>Gerenciamento de Cache</h3>
                
                {cacheError && <p className="error-message">{cacheError}</p>}
                {cacheMessage && <p className="success-message">{cacheMessage}</p>}
                
                <p style={{color: 'var(--color-text-secondary)', marginBottom: '15px'}}>
                    Limpar o cache força o sistema a re-analisar todos os sites na próxima vez que forem solicitados.
                </p>
                
                <button
                    onClick={handleClearCache}
                    className="danger-button"
                    disabled={isClearingCache}
                    style={{width: 'auto'}}
                >
                    {isClearingCache ? 'Limpando...' : 'Limpar Todo o Cache de Scrape'}
                </button>
            </div>
           

           
            <div className="admin-widget">
                <h3>Utilizadores Existentes</h3>
                <table className="table">
                    <thead>
                        <tr>
                            <th>Email</th>
                            <th>Admin?</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>{user.email}</td>
                                <td>{user.is_admin ? 'Sim' : 'Não'}</td>
                                <td>
                                    <button onClick={() => handleDeleteUser(user.id)} className="danger-button">
                                        Deletar
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminPage;
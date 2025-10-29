import React from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import './App.css'; // O nosso CSS

// Nossas Páginas
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage'; // <-- 1. IMPORTAR A NOVA PÁGINA
import DashboardPage from './pages/DashboardPage';
import AdminPage from './pages/AdminPage'; 

// Nosso "Porteiro"
import AdminRoute from './components/AdminRoute';

// Componente de Layout (Navbar)
const Layout = ({ children }) => {
    const { isAuthenticated, isAdmin, logout } = useAuth();
    
    return (
        <div className="layout-container">
            {isAuthenticated && (
                <nav className="navbar">
                    <Link to="/" className="navbar-link">Dashboard (Scraping)</Link>
                    {isAdmin && (
                        <Link to="/admin" className="navbar-link">Painel de Admin</Link>
                    )}
                    <a href="#" onClick={logout} className="navbar-logout">Sair</a>
                </nav>
            )}
            <main className="main-content">
                {children}
            </main>
        </div>
    );
};


function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Layout>
      <Routes>
        <Route 
          path="/login" 
          element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" replace />} 
        />
        
        {/* --- 2. ADICIONAR A NOVA ROTA --- */}
        <Route 
          path="/register" 
          element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/" replace />} 
        />
        
        <Route 
          path="/" 
          element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" replace />} 
        />

        <Route path="/admin" element={<AdminRoute />}>
          <Route path="" element={<AdminPage />} /> 
        </Route>
      </Routes>
    </Layout>
  );
}

export default App;
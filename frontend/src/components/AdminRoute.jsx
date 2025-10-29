import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate, Outlet } from 'react-router-dom';

const AdminRoute = () => {
    const { isAuthenticated, isAdmin } = useAuth(); // Pega o status do "cérebro"

    if (!isAuthenticated) {
        // 1. Se não está logado, expulsa para o login
        return <Navigate to="/login" replace />;
    }

    if (!isAdmin) {
        // 2. Se está logado, MAS NÃO É ADMIN, expulsa para o dashboard
        return <Navigate to="/" replace />;
    }

    // 3. Se está logado E É ADMIN, permite o acesso
    return <Outlet />;
};

export default AdminRoute;
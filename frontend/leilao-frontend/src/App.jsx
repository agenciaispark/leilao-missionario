import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Toaster } from '@/components/ui/toaster';
import Home from './pages/Home';
import ItemDetails from './pages/ItemDetails';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import './App.css';

// Componente para proteger rotas privadas
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return user ? children : <Navigate to="/admin" />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Rotas Públicas */}
          <Route path="/" element={<Home />} />
          <Route path="/item/:id" element={<ItemDetails />} />
          
          {/* Rotas Administrativas */}
          <Route path="/admin" element={<Login />} />
          <Route
            path="/admin/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/campanhas"
            element={
              <PrivateRoute>
                <div className="p-8 text-center">
                  <h1 className="text-2xl font-bold">Gerenciamento de Campanhas</h1>
                  <p className="text-gray-600 mt-2">Em desenvolvimento</p>
                </div>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/itens"
            element={
              <PrivateRoute>
                <div className="p-8 text-center">
                  <h1 className="text-2xl font-bold">Gerenciamento de Itens</h1>
                  <p className="text-gray-600 mt-2">Em desenvolvimento</p>
                </div>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/lances"
            element={
              <PrivateRoute>
                <div className="p-8 text-center">
                  <h1 className="text-2xl font-bold">Gerenciamento de Lances</h1>
                  <p className="text-gray-600 mt-2">Em desenvolvimento</p>
                </div>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/categorias"
            element={
              <PrivateRoute>
                <div className="p-8 text-center">
                  <h1 className="text-2xl font-bold">Gerenciamento de Categorias</h1>
                  <p className="text-gray-600 mt-2">Em desenvolvimento</p>
                </div>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin/usuarios"
            element={
              <PrivateRoute>
                <div className="p-8 text-center">
                  <h1 className="text-2xl font-bold">Gerenciamento de Usuários</h1>
                  <p className="text-gray-600 mt-2">Em desenvolvimento</p>
                </div>
              </PrivateRoute>
            }
          />
        </Routes>
        <Toaster />
      </Router>
    </AuthProvider>
  );
}

export default App;

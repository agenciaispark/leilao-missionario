import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, TrendingUp, Package, Gavel, DollarSign, LogOut } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/admin');
      return;
    }
    loadDashboard();
  }, [user, navigate]);

  const loadDashboard = async () => {
    try {
      const dashboardData = await api.getDashboard();
      setData(dashboardData);
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível carregar os dados do dashboard.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/admin');
    toast({
      title: 'Logout realizado',
      description: 'Você foi desconectado com sucesso.',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-sm text-gray-600">Bem-vindo, {user?.nome}</p>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={() => navigate('/')}
              >
                Ver Site Público
              </Button>
              <Button
                variant="ghost"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="py-4 px-1 border-b-2 border-primary font-medium text-sm text-primary"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/admin/campanhas')}
              className="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              Campanhas
            </button>
            <button
              onClick={() => navigate('/admin/itens')}
              className="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              Itens
            </button>
            <button
              onClick={() => navigate('/admin/lances')}
              className="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              Lances
            </button>
            {user?.permissao === 'admin' && (
              <>
                <button
                  onClick={() => navigate('/admin/categorias')}
                  className="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Categorias
                </button>
                <button
                  onClick={() => navigate('/admin/usuarios')}
                  className="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  Usuários
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Campanhas Ativas
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data?.campanhas_ativas || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total de Itens
              </CardTitle>
              <Package className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data?.total_itens || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total de Lances
              </CardTitle>
              <Gavel className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data?.total_lances || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Valor Arrecadado
              </CardTitle>
              <DollarSign className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                R$ {data?.valor_arrecadado?.toFixed(2) || '0.00'}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Últimos Lances */}
        <Card>
          <CardHeader>
            <CardTitle>Últimos Lances</CardTitle>
          </CardHeader>
          <CardContent>
            {data?.ultimos_lances && data.ultimos_lances.length > 0 ? (
              <div className="space-y-4">
                {data.ultimos_lances.map((lance) => (
                  <div
                    key={lance.id}
                    className="flex items-center justify-between py-3 border-b last:border-0"
                  >
                    <div>
                      <p className="font-semibold">{lance.item.nome}</p>
                      <p className="text-sm text-gray-600">
                        {lance.nome_participante} - {lance.telefone}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg text-primary">
                        R$ {lance.valor.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(lance.data_lance).toLocaleString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">
                Nenhum lance registrado ainda.
              </p>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

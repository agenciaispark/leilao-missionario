import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [itens, setItens] = useState([]);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [itensData, configData] = await Promise.all([
        api.getItens(),
        api.getConfiguracoes()
      ]);
      setItens(itensData);
      setConfig(configData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {config?.nome_instituicao || 'Leilão Missionário'}
              </h1>
              <p className="text-gray-600 mt-1">
                {config?.mensagem_home || 'Participe e contribua com nossa missão!'}
              </p>
            </div>
            <button
              onClick={() => navigate('/admin')}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Área Administrativa
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {itens.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              Nenhum item disponível no momento.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {itens.map((item) => (
              <Card
                key={item.id}
                className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/item/${item.id}`)}
              >
                <CardContent className="p-0">
                  <div className="md:flex">
                    {/* Banner */}
                    <div className="md:w-2/5 bg-gray-200 aspect-video md:aspect-auto">
                      {item.banner_16_9 ? (
                        <img
                          src={item.banner_16_9}
                          alt={item.nome}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          Sem imagem
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="md:w-3/5 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            {item.nome}
                          </h2>
                          <Badge variant="secondary" className="mb-2">
                            {item.categoria.nome}
                          </Badge>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Lance Atual</p>
                          <p className="text-4xl font-bold text-primary">
                            {config?.moeda || 'R$'} {item.lance_atual.toFixed(2)}
                          </p>
                        </div>

                        <div className="pt-4">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/item/${item.id}`);
                            }}
                            className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
                          >
                            Ver Detalhes e Dar Lance
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              {config?.nome_instituicao || 'Leilão Missionário'}
            </p>
            {config?.telefone && (
              <p className="text-gray-400 mt-1">
                Telefone: {config.telefone}
              </p>
            )}
            {config?.email && (
              <p className="text-gray-400 mt-1">
                Email: {config.email}
              </p>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

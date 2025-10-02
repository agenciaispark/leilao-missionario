import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function ItemDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [item, setItem] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    valor: '',
    nome_participante: '',
    telefone: ''
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [itemData, configData] = await Promise.all([
        api.getItem(id),
        api.getConfiguracoes()
      ]);
      setItem(itemData);
      setConfig(configData);
      // Define o valor mínimo do lance
      setFormData(prev => ({
        ...prev,
        valor: (itemData.lance_atual + 0.01).toFixed(2)
      }));
    } catch (error) {
      console.error('Erro ao carregar item:', error);
      toast({
        title: 'Erro',
        description: 'Não foi possível carregar os dados do item.',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'telefone') {
      // Máscara de telefone: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
      const cleaned = value.replace(/\D/g, '');
      let formatted = cleaned;
      
      if (cleaned.length <= 11) {
        if (cleaned.length > 6) {
          formatted = `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, cleaned.length === 11 ? 7 : 6)}-${cleaned.slice(cleaned.length === 11 ? 7 : 6)}`;
        } else if (cleaned.length > 2) {
          formatted = `(${cleaned.slice(0, 2)}) ${cleaned.slice(2)}`;
        } else if (cleaned.length > 0) {
          formatted = `(${cleaned}`;
        }
      }
      
      setFormData(prev => ({ ...prev, [name]: formatted }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validações
    if (!formData.nome_participante.trim()) {
      toast({
        title: 'Erro',
        description: 'Por favor, informe seu nome.',
        variant: 'destructive'
      });
      return;
    }

    const telefoneClean = formData.telefone.replace(/\D/g, '');
    if (telefoneClean.length < 10) {
      toast({
        title: 'Erro',
        description: 'Por favor, informe um telefone válido.',
        variant: 'destructive'
      });
      return;
    }

    const valorNumerico = parseFloat(formData.valor);
    if (isNaN(valorNumerico) || valorNumerico <= item.lance_atual) {
      toast({
        title: 'Erro',
        description: `O lance deve ser maior que ${config?.moeda || 'R$'} ${item.lance_atual.toFixed(2)}`,
        variant: 'destructive'
      });
      return;
    }

    setSubmitting(true);

    try {
      await api.createLance({
        item_id: parseInt(id),
        valor: valorNumerico,
        nome_participante: formData.nome_participante,
        telefone: formData.telefone
      });

      toast({
        title: 'Lance registrado!',
        description: 'Seu lance foi registrado com sucesso.',
      });

      // Recarrega os dados do item
      await loadData();

      // Limpa o formulário
      setFormData({
        valor: (valorNumerico + 0.01).toFixed(2),
        nome_participante: '',
        telefone: ''
      });
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.message || 'Não foi possível registrar o lance.',
        variant: 'destructive'
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-500 mb-4">Item não encontrado.</p>
        <Button onClick={() => navigate('/')}>Voltar para Home</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Voltar
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {config?.nome_instituicao || 'Leilão Missionário'}
          </h1>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Imagem e Informações */}
          <div>
            <Card>
              <CardContent className="p-0">
                <div className="aspect-video bg-gray-200">
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
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {item.nome}
                  </h2>
                  <Badge variant="secondary" className="mb-4">
                    {item.categoria.nome}
                  </Badge>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-gray-600">Campanha</p>
                      <p className="font-semibold">{item.campanha.nome}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Lance Inicial</p>
                      <p className="font-semibold">
                        {config?.moeda || 'R$'} {item.lance_inicial.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Últimos Lances */}
            {item.ultimos_lances && item.ultimos_lances.length > 0 && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Últimos Lances</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {item.ultimos_lances.map((lance, index) => (
                      <div
                        key={index}
                        className="flex justify-between items-center py-2 border-b last:border-0"
                      >
                        <span className="font-semibold">
                          {config?.moeda || 'R$'} {lance.valor.toFixed(2)}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(lance.data).toLocaleString('pt-BR')}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Formulário de Lance */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Dar Lance</CardTitle>
                <p className="text-sm text-gray-600 mt-2">
                  Lance Atual: <span className="text-3xl font-bold text-primary">
                    {config?.moeda || 'R$'} {item.lance_atual.toFixed(2)}
                  </span>
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="valor">Valor do Lance *</Label>
                    <Input
                      id="valor"
                      name="valor"
                      type="number"
                      step="0.01"
                      min={item.lance_atual + 0.01}
                      value={formData.valor}
                      onChange={handleInputChange}
                      required
                      placeholder="0.00"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Valor mínimo: {config?.moeda || 'R$'} {(item.lance_atual + 0.01).toFixed(2)}
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="nome_participante">Nome Completo *</Label>
                    <Input
                      id="nome_participante"
                      name="nome_participante"
                      type="text"
                      value={formData.nome_participante}
                      onChange={handleInputChange}
                      required
                      placeholder="Seu nome completo"
                    />
                  </div>

                  <div>
                    <Label htmlFor="telefone">Telefone *</Label>
                    <Input
                      id="telefone"
                      name="telefone"
                      type="tel"
                      inputMode="numeric"
                      value={formData.telefone}
                      onChange={handleInputChange}
                      required
                      placeholder="(00) 00000-0000"
                      maxLength={15}
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Registrando...
                      </>
                    ) : (
                      'Registrar Lance'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

CREATE TABLE campanhas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    ano INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ativa', 'finalizada', 'arquivada')),
    banner VARCHAR(255)
);

CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE itens (
    id SERIAL PRIMARY KEY,
    campanha_id INTEGER NOT NULL REFERENCES campanhas(id),
    nome VARCHAR(255) NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    banner_16_9 VARCHAR(255),
    banner_1_1 VARCHAR(255),
    lance_inicial NUMERIC(10, 2) NOT NULL
);

CREATE TABLE lances (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES itens(id),
    valor NUMERIC(10, 2) NOT NULL,
    nome_participante VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    data_lance TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL, -- Armazenar hash da senha
    permissao VARCHAR(50) NOT NULL CHECK (permissao IN ('admin', 'gestor', 'operador'))
);

CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    acao TEXT NOT NULL,
    data_acao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE configuracoes (
    id SERIAL PRIMARY KEY,
    nome_instituicao VARCHAR(255),
    logo VARCHAR(255),
    telefone VARCHAR(20),
    email VARCHAR(255),
    moeda VARCHAR(10) DEFAULT 'R$',
    mensagem_home TEXT
);

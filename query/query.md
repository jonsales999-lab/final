use ecoplay;
select * from tarefas;
select * from usuarios;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE execucoes_tarefas_aprovacoes;
TRUNCATE TABLE execucoes_tarefas;
TRUNCATE TABLE membros_equipes;
TRUNCATE TABLE equipes;
TRUNCATE TABLE tarefas;
TRUNCATE TABLE usuarios;
-- (adicione outras tabelas conforme necessário)
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO tarefas (titulo, descricao, pontuacao) VALUES
('Captação garrafa PET', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 10),
('Captação embalagem longa vida (leite/suco/outros)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 20),
('Captação garrafa de vidro (vinho, cerveja, azeite)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 10),
('Captação celular com defeito', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 20),
('Captação latinha de alumínio', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 50),
('Captação lacre de alumínio (latinhas)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 30),
('Captação folha A4 rascunho', 'Deixar coletor em escritórios - Fazer a coleta 3x por semana', 30),
('Captação roupas e calçados usados', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 5),
('Captação cartela de comprimido (cartela vazia)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 10),
('Captação embalagem aerosol', '-', 15),
('Captação copo plástico descartável', 'Deixar coletor em escritórios - Fazer a coleta 3x por semana', 20),
('Captação pneu usado', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 15),
('Captação revistas e jornais', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 25),
('Captação óleo de fritura usado', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 50),
('Captação livro usado', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 10),
('Captação pilhas usadas', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 5),
('Captação monitor - Notebook, PC ou TV', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 20),
('Captação CPU - PC ou notebook', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 25),
('Captação bituca de cigarro', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 5),
('Captação cápsula de café', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 10),
('Captação tampinha de plástico', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 30),
('Captação tampinha de metal', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 30),
('Captação marmita/bandeja de Isopor', 'Deixar coletor em residências e restaurantes - Fazer a coleta 3x por semana', 30),
('Captação chapa de Isopor (pedaços)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 30),
('Captação talher e pratinho plástico (festa)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 20),
('Captação kit tintura cabelo (frascos)', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 50),
('Captação bateria de celular – usadas', 'Deixar coletor em residências e condomínios - Fazer a coleta 3x por semana', 25),
('Distribuir coletores seletivos', 'Distribuição em residências e condomínios', 10),
('Advertências à motoristas', 'Monitorar o trânsito em avenidas - com semáforos - fumaça preta/cano de descarga - Entregar ticket', 15),
('Ação em postos de combustíveis', 'Atenção aos postos da Lista (explicar a emissão de co2) - Convencer a escolher Etanol - Entregar flyer', 20),
('Advertências à fumantes que jogam cigarro no chão', 'Monitorar alvos em ruas movimentadas - Entregar Cartilha/Ticket', 10),
('Palestras em ônibus coletivos sobre preservação do meio ambiente', 'Escolher uma linha movimentada, porém, com espaço interno para se posicionar e captar a atenção dos passageiros - Entregar Cartilha', 20),
('Palestras em metrô de BH/Contagem sobre preservação do meio ambiente', 'Escolher um horário menos tumultuado e um vagão com espaço interno para se posicionar e captar a atenção dos passageiros - Entregar Cartilha', 20),
('Palestras em escolas públicas e privadas sobre preservação do meio ambiente', 'Ligar para a diretoria e agendar dia e horário - Pedir para os professores divulgarem - Lembrar a diretora 01 dia antes - Entregar Cartilha', 20),
('Citar de Cor a Declaração Universal dos Direitos da Água', 'Ler com atenção e decorar o texto', 30),
('Citar os tipos de materiais recicláveis e não recicláveis existentes no mercado', 'Ler com atenção e decorar o texto', 10),
('Citar de Cor os significados das siglas dos Recicláveis (PEAD, PEBD, PVC, PET, etc...)', 'Ler com atenção e decorar o texto', 10),
('Plantar mudas (espécies a indicar)', 'Escolher local autorizado mais próximo para a equipe - Agendar dia e horário', 10),
('Realizar passeio ciclístico (panfletagem sobre opção da bicicleta)', 'Escolher local autorizado mais próximo para a equipe - Agendar dia e horário - Distribuir Cartilhas', 35),
('Visita e inspeção básica em Madeireiras, gráficas e postos de combustíveis', 'Escolher local mais próximo para a equipe - Visita surpresa', 25),
('Conseguir incluir matérias e/ou entrevistas em veículos de comunicação', 'Escolher veículos com antecedência - Ligar para a redação, explicar e convencer', 50),
('Escrever e encenar uma peça teatral de apelo à preservação', 'Combinar equipe - Ensaiar - Selecionar local com movimentação (supermercados, igrejas)', 50),
('Redigir Carta Aberta à indústria, comércio e população', 'Combinar equipe - Escolher empresas da lista - Enviar', 40),
('Ato Pacífico em frente lojas "Cadê a Logística Reversa?"', 'Selecionar empresas da lista - Agendar com a equipe dia e horário', 40),
('Pedágio em semáforos', 'Atenção aos semáforos da Lista - Distribuir lixocar e mudas', 30),
('Lavar automóveis (exterior) com água de reuso/chuva', 'Estacionamento de condomínios e supermercados - Pedir autorização ao proprietário', 20),
('Lavar automóveis a seco (exterior) - produtos ecológicos', 'Estacionamento de condomínios e supermercados - Pedir autorização ao proprietário', 25),
('Limpeza de córrego, lagoa, nascente, lote vago, terreno baldio', 'Escolher locais na lista - Agendar dia e horário - Levar acessórios de proteção', 30),
('Limpeza de córrego, lagoa, nascente, lote vago, terreno baldio', 'Escolher locais na lista - Agendar dia e horário - Levar acessórios de proteção', 20),
('Lavar calçadas - mínimo de água/sabão', 'Abordar donas de casa e pedir autorização', 15),
('DUCHA RÁPIDA – Masculino / Feminino', 'Definir componente - Ligar para condomínios e pedir autorização - Entregar cartilha educativa - Selecionar semáforos longos - Agendar locais públicos', 50),
('Fabricar papel reciclado artesanalmente', 'Assistir vídeo - Preparar equipamentos - Juntar papel - Fazer em conjunto com a equipe', 20),
('Criar acessórios, brinquedos e objetos de arte/utilidade com descartados', 'Assistir vídeo de instrução', 50),
('Montar o quebra-cabeça gigante', 'Reservar dia e horário com a Produção', 50),
('Criar mesas/cadeiras com pneus usados', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Criar placa rígida a partir de embalagens longa vida', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Criar telhas ecológicas a partir de embalagens longa vida', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Criar luminárias a partir de caixinhas de leite/suco', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Criar Abajours a partir de garrafas usadas', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Criar Racks a partir de pallets', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 50),
('Produção de Biogás', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 80),
('Produção de Adubo orgânico', 'Assistir vídeo - Reservar dia e horário na cooperativa parceira - Participação coletiva', 70);


INSERT INTO escolas (nome, endereco, cidade, estado, cep, telefone, email) VALUES
('Escola Municipal Sol Nascente', 'Rua das Flores, 100', 'Cidade Nova', 'SP', '12345-000', '(11) 1234-5678', 'solnascente@escola.com'),
('Colégio Novo Saber', 'Av. Central, 200', 'Bela Vista', 'RJ', '23456-111', '(21) 2345-6789', 'novosaber@colegio.com'),
('Escola Estadual Horizonte Azul', 'Rua do Horizonte, 300', 'Horizonte', 'MG', '34567-222', '(31) 3456-7890', 'horizonteazul@escola.com'),
('Instituto Educacional Vida Nova', 'Av. das Palmeiras, 400', 'Palmeiras', 'RS', '45678-333', '(51) 4567-8901', 'vidanova@instituto.com'),
('Escola Criativa do Futuro', 'Rua do Futuro, 500', 'Futuria', 'PR', '56789-444', '(41) 5678-9012', 'criativafuturo@escola.com'),
('Centro Educacional Sementes do Amanhã', 'Av. das Sementes, 600', 'Sementeira', 'SC', '67890-555', '(48) 6789-0123', 'sementes@centro.com'),
('Escola Integração Total', 'Rua da Integração, 700', 'Integração', 'BA', '78901-666', '(71) 7890-1234', 'integracaototal@escola.com'),
('Colégio Pioneiros do Saber', 'Av. dos Pioneiros, 800', 'Pioneira', 'GO', '89012-777', '(62) 8901-2345', 'pioneiros@colegio.com'),
('Escola Comunitária Esperança Viva', 'Rua da Esperança, 900', 'Esperança', 'PE', '90123-888', '(81) 9012-3456', 'esperancaviva@escola.com'),
('Instituto Aprender e Crescer', 'Av. do Aprendizado, 1000', 'Aprendiz', 'CE', '01234-999', '(85) 0123-4567', 'aprendercrescer@instituto.com');
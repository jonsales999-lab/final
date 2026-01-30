-- Mapeamento de Unidades (Sugestão de IDs):
-- 1: KG, 2: Litros, 3: M³, 4: UN, 5: Ação

INSERT INTO tarefas (titulo, descricao, pontuacao, unidade_id, material_id) VALUES
-- TAREFAS POR KG (unidade_id: 1)
('Coleta de garrafa PET', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 10, 1, 'garrafa_pet'),
('Coleta de embalagem longa vida (leite/suco/outros)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 20, 1, 'embalagem_longa_vida'),
('Coleta de garrafa de vidro (vinho, cerveja, azeite)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 10, 1, 'garrafa_de_vidro'),
('Coleta de latinha de aluminio', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 50, 1, 'latinha'),
('Coleta de lacre de aluminio (latinhas)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 30, 1, 'lacre_aluminio'),
('Coleta de folha A4 rascunho', 'Deixar coletor em escritorios - Fazer a coleta 3x por semana', 30, 1, 'folha_A4'),
('Coleta de copo plastico descartavel', 'Deixar coletor em escritorios - Fazer a coleta 3x por semana', 20, 1, 'copo_plastico'),
('Coleta de revistas e jornais', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 25, 1, 'revistas_jornais'),
('Coleta de capsula de cafe', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 10, 1, 'capsula_cafe'),
('Coleta de tampinha de plastico', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 30, 1, 'tampinha_plastico'),
('Coleta de tampinha de metal', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 30, 1, 'tampinha_metal'),
('Coleta de marmita/bandeja de Isopor', 'Deixar coletor em residencias e restaurantes - Fazer a coleta 3x por semana', 30, 1, 'marmita_isopor'),
('Coleta de chapa de Isopor (pedacos)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 30, 1, 'isopor'),
('Coleta de talher e pratinho plastico (festa)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 20, 1, 'talher_pratinho_plastico'),
('Coleta de kit tintura cabelo (frascos)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 50, 1, 'frascos_tintura_cabelo'),
('Limpeza de corrego, lagoa, nascente, lote vago, terreno baldio', 'Escolher locais na lista - Agendar dia e horario - Levar acessorios de protecao', 30, 1, 'limpeza_corrego'),
('Fabricar papel reciclado artesanalmente', 'Assistir video - Preparar equipamentos - Juntar papel - Fazer em conjunto com a equipe', 20, 1, 'papel_reciclado'),
('Producao de Adubo organico', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 70, 1, 'adubo_organico'),

-- TAREFAS POR LITROS (unidade_id: 2)
('Coleta de oleo de fritura usado', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 50, 2, 'oleo_fritura'),

-- TAREFAS POR M³ (unidade_id: 3)
('Producao de Biogas', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 80, 3, 'biogas'),

-- TAREFAS POR UN (unidade_id: 4)
('Coleta de celular com defeito', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 20, 4, 'celular'),
('Coleta de roupas e calcados usados', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 5, 4, 'roupas'),
('Coleta de cartela de comprimido (cartela vazia)', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 10, 4, 'cartela_comprimido'),
('Coleta de embalagem aerosol', 'Coletar embalagem de aerosol', 15, 4, 'aerosol'),
('Coleta de pneu usado', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 15, 4, 'pneu_usado'),
('Coleta de livro usado', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 10, 4, 'livro_usado'),
('Coleta de pilhas usadas', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 5, 4, 'pilha_usada'),
('Coleta de monitor - Notebook, PC ou TV', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 20, 4, 'monitor_pc_tv'),
('Coleta de CPU - PC ou notebook', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 25, 4, 'cpu_notebook'),
('Coleta de bituca de cigarro', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 5, 4, 'bituca'),
('Coleta de bateria de celular – usadas', 'Deixar coletor em residencias e condominios - Fazer a coleta 3x por semana', 25, 4, 'bateria_celular'),
('Distribuir coletores seletivos', 'Distribuicao em residencias e condominios', 10, 4, 'coletor_seletivo'),
('Criar acessorios, brinquedos e objetos de arte/utilidade com descartados', 'Assistir video de instrucao', 50, 4, NULL),
('Montar o quebra-cabeca gigante', 'Reservar dia e horario com a Producao', 50, 4, 'quebracabeca'),
('Criar mesas/cadeiras com pneus usados', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, 'mesa_cadeira_pneu'),
('Criar placa rigida a partir de embalagens longa vida', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, 'placa_rigida'),
('Criar telhas ecologicas a partir de embalagens longa vida', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, 'telha_ecologica'),
('Criar luminarias a partir de caixinhas de leite/suco', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, 'luminaria'),
('Criar Abajours a partir de garrafas usadas', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, 'abajour'),
('Criar Racks a partir de pallets', 'Assistir video - Reservar dia e horario na cooperativa parceira - Participacao coletiva', 50, 4, NULL),

-- TAREFAS POR ACAO (unidade_id: 5)
('Advertencias a motoristas', 'Monitorar o transito em avenidas - com semaforos - fumaca preta/cano de descarga - Entregar ticket', 15, 5, NULL),
('Acao em postos de combustiveis', 'Atencao aos postos da Lista (explicar a emissao de co2) - Convencer a escolher Etanol - Entregar flyer', 20, 5, NULL),
('Advertencias a fumantes que jogam cigarro no chao', 'Monitorar alvos em ruas movimentadas - Entregar Cartilha/Ticket', 10, 5, NULL),
('Palestras em onibus coletivos sobre preservacao do meio ambiente', 'Escolher uma linha movimentada, porem, com espaco interno para se posicionar e captar a atencao dos passageiros - Entregar Cartilha', 20, 5, NULL),
('Palestras em metro de BH/Contagem sobre preservacao do meio ambiente', 'Escolher um horario menos tumultuado e um vagao com espaco interno para se posicionar e captar a atencao dos passageiros - Entregar Cartilha', 20, 5, NULL),
('Palestras em escolas publicas e privadas sobre preservacao do meio ambiente', 'Ligar para a diretoria e agendar dia e horario - Pedir para os professores divulgarem - Lembrar a diretora 01 dia antes - Entregar Cartilha', 20, 5, NULL),
('Citar de Cor a Declaracao Universal dos Direitos da Agua', 'Ler com atencao e decorar o texto', 30, 5, NULL),
('Citar os tipos de materiais reciclaveis e nao reciclaveis existentes no mercado', 'Ler com atencao e decorar o texto', 10, 5, NULL),
('Citar de Cor os significados das siglas dos Reciclaveis (PEAD, PEBD, PVC, PET, etc...)', 'Ler com atencao e decorar o texto', 10, 5, NULL),
('Plantar mudas (especies a indicar)', 'Escolher local autorizado mais proximo para a equipe - Agendar dia e horario', 10, 5, NULL),
('Realizar passeio ciclistico (panfletagem sobre opcao da bicicleta)', 'Escolher local autorizado mais proximo para a equipe - Agendar dia e horario - Distribuir Cartilhas', 35, 5, NULL),
('Visita e inspecao basica em Madeireiras, graficas e postos de combustiveis', 'Escolher local mais proximo para a equipe - Visita surpresa', 25, 5, NULL),
('Conseguir incluir materias e/ou entrevistas em veiculos de comunicacao', 'Escolher veiculos com antecedencia - Ligar para a redacao, explicar e convencer', 50, 5, NULL),
('Escrever e encenar uma peca teatral de apelo a preservacao', 'Combinar equipe - Ensaiar - Selecionar local com movimentacao (supermercados, igrejas)', 50, 5, NULL),
('Redigir Carta Aberta a industria, comercio e populacao', 'Combinar equipe - Escolher empresas da lista - Enviar', 40, 5, NULL),
('Ato Pacifico em frente lojas "Cade a Logistica Reversa?"', 'Selecionar empresas da lista - Agendar com a equipe dia e horario', 40, 5, NULL),
('Pedagio em semaforos', 'Atencao aos semaforos da Lista - Distribuir lixocar e mudas', 30, 5, NULL),
('Lavar automoveis (exterior) com agua de reuso/chuva', 'Estacionamento de condominios e supermercados - Pedir autorizacao ao proprietario', 20, 5, NULL),
('Lavar automoveis a seco (exterior) - produtos ecologicos', 'Estacionamento de condominios e supermercados - Pedir autorizacao ao proprietario', 25, 5, NULL),
('Lavar calcadas - minimo de agua/sabao', 'Abordar donas de casa e pedir autorizacao', 15, 5, NULL),
('DUCHA RAPIDA – Masculino / Feminino', 'Definir componente - Ligar para condominios e pedir autorizacao - Entregar cartilha educativa - Selecionar semaforos longos - Agendar locais publicos', 50, 5, NULL);


KG
garrafa PET 
embalagem longa vida
garrafa de vidro
latinha de alumínio
lacre de alumínio
folha A4 rascunho
copo plástico descartável
revistas e jornais
cápsula de café
tampinha de plástico
tampinha de metal
marmita/bandeja de Isopor
chapa de Isopor (pedaços)
talher e pratinho plástico (festa)
kit tintura cabelo (frascos)
Limpeza de córrego, lagoa, nascente, lote vago, terreno baldio
papel reciclado artesanalmente
Produção de Adubo orgânico

Litros
óleo de fritura usado

M³

Produção de Biogás 



Tarefas por UN


Captação celular com defeito
Captação roupas e calçados usados 
Captação cartela de comprimido
Captação embalagem aerossol
Captação pneu usado
Captação livro usado
Captação pilhas usadas
Captação monitor - Notebook, PC ou TV
Captação CPU - PC ou notebook
Captação bituca de cigarro
Captação bateria de celular
Distribuir coletores seletivos
Criar acessórios, brinquedos e objetos de arte/utilidade com descartados
Montar o quebra-cabeça gigante
Criar mesas/cadeiras com pneus usados
Criar placa rígida a partir de embalagens longa vida
Criar telhas ecológicas a partir de embalagens longa vida
Criar luminárias a partir de caixinhas de leite/suco
Criar Abajours a partir de garrafas usadas
Criar Racks a partir de pallets

Tarefas por ação

Advertências à motoristas
Ação em postos de combustíveis
Advertências à fumantes que jogam cigarro no chão
Palestras em ônibus coletivos sobre preservação do meio ambiente
Palestras em metrô de BH/Contagem sobre preservação do meio ambiente
Palestras em escolas públicas e privadas sobre preservação do meio ambiente
Citar de Cor a Declaração Universal dos Direitos da Água Ler com atenção e decorar o texto
Citar os tipos de materiais recicláveis e não recicláveis existentes no mercado
Citar de Cor os significados das siglas dos Recicláveis
Realizar passeio ciclístico
Visita e inspeção básica em Madeireiras, gráficas e postos de combustíveis
Conseguir incluir matérias e/ou entrevistas em veículos de comunicação
Escrever e encenar uma peça teatral de apelo à preservação
Combinar equipe - Ensaiar - Selecionar local com movimentação 
Redigir Carta Aberta à indústria, comércio e população
Ato Pacífico em frente lojas “Cadê a Logística Reversa?
Pedágio em semáforos
Lavar automóveis (exterior) com água de reuso/chuva
Lavar automóveis a seco (exterior) - produtos ecológicos
Lavar calçadas - mínimo de água/sabão
DUCHA RÁPIDA – Masculino / Feminino 
Analise de Risco de Credito com Machine Learning

Descricao do Projeto

Este projeto tem como objetivo prever a inadimplencia de clientes solicitantes de credito, utilizando tecnicas de analise exploratoria de dados, tratamento e limpeza, engenharia de atributos e dois modelos de classificacao: K-Nearest Neighbors (KNN) e Arvore de Decisao. Alem da construcao dos modelos, o projeto conduz um diagnostico de overfitting e uma avaliacao final orientada ao impacto financeiro dos erros de classificacao, concluindo com a recomendacao do modelo mais adequado para uso em producao.

O trabalho foi desenvolvido como projeto avaliativo do Modulo 1 da disciplina de Fundamentos de Programacao, Dados e Machine Learning.

Arquivos do Projeto

O projeto e composto pelos seguintes arquivos:

credit_risk_project.ipynb, que contem todo o desenvolvimento do projeto, do carregamento dos dados ate a avaliacao final dos modelos.

credit_risk_dataset.csv, que contem a base de dados original utilizada em todas as etapas do projeto.

README.md, que e o presente documento, com a descricao geral do projeto.

Descricao da Base de Dados

A base de dados utilizada e o arquivo credit_risk_dataset.csv, composta por 32.581 registros de solicitantes de credito, distribuidos em 12 colunas. As variaveis podem ser agrupadas da seguinte forma.

Dados pessoais do solicitante: idade, renda anual, situacao de moradia e tempo de emprego.

Dados do emprestimo solicitado: finalidade do emprestimo, classificacao de risco atribuida pela instituicao, valor solicitado, taxa de juros e percentual da renda comprometido.

Historico de credito do solicitante: existencia de inadimplencia anterior registrada e tempo de historico de credito.

Variavel alvo: status do emprestimo, que indica se o cliente pagou o emprestimo em dia ou se houve inadimplencia.

Estrutura do Projeto

O notebook esta organizado em seis fases sequenciais, descritas a seguir.

Fase 1, Analise Exploratoria de Dados. Nesta fase sao apresentados o tamanho da base, os tipos de dados de cada coluna e o resumo estatistico descritivo. Sao construidos graficos de distribuicao das principais variaveis numericas, um grafico da proporcao entre clientes adimplentes e inadimplentes, e um mapa de correlacao de Pearson entre as variaveis numericas. Ao final desta fase e apresentado um paragrafo de interpretacao dos resultados, que orienta as decisoes tomadas nas fases seguintes.

Fase 2, Tratamento e Limpeza dos Dados. Nesta fase sao identificadas e removidas linhas duplicadas. Os valores ausentes sao tratados de forma distinta conforme a distribuicao de cada variavel, utilizando a mediana para variaveis com distribuicao assimetrica e a media para variaveis com distribuicao proxima da simetrica. Tambem sao identificados e removidos registros com valores fisicamente impossiveis, como idade acima de cem anos e tempo de emprego acima de sessenta anos, os quais sao tratados como erros de preenchimento e nao como variacoes legitimas dos dados.

Fase 3, Engenharia de Atributos. Nesta fase e criada uma nova coluna numerica, denominada comprometimento_renda, calculada como a razao entre o valor do emprestimo solicitado e a renda anual do cliente, multiplicada por cem. O tratamento dos valores ausentes das colunas originais e realizado antes deste calculo, de modo a evitar a geracao de valores invalidos.

Fase 4, Separacao dos Dados, Balanceamento e Escalonamento. Nesta fase as variaveis categoricas sao convertidas em formato numerico. A coluna de classificacao de risco do emprestimo, que possui uma ordem natural entre suas categorias, e convertida por meio de um mapeamento numerico explicito. As demais variaveis categoricas, que nao possuem ordem natural entre si, sao convertidas por meio de codificacao one hot. Em seguida, os dados sao divididos em conjunto de treino e conjunto de teste, de forma estratificada, preservando a proporcao original da variavel alvo em ambos os conjuntos. O balanceamento das classes e aplicado exclusivamente no conjunto de treino, por meio de subamostragem aleatoria da classe majoritaria, de modo a evitar o vazamento de informacao para o conjunto de teste. O escalonamento das variaveis numericas e aplicado apenas para o modelo KNN, uma vez que este modelo depende de distancia entre os pontos, enquanto o modelo de Arvore de Decisao dispensa este tratamento, pois realiza suas divisoes por meio de limiares que nao sao afetados pela escala das variaveis.

Fase 5, Modelagem e Diagnostico de Overfitting. Nesta fase sao realizados diversos testes de configuracao para os dois modelos. Para o KNN, e testada a variacao do numero de vizinhos considerados. Para a Arvore de Decisao, e testada a variacao da profundidade maxima permitida. Em ambos os casos, o desempenho e comparado entre o conjunto de treino e o conjunto de teste, permitindo identificar em qual configuracao ocorre overfitting, isto e, quando o modelo memoriza o conjunto de treino em vez de aprender um padrao generalizavel.

Fase 6, Avaliacao Final e Analise de Negocio. Nesta fase sao selecionadas as melhores configuracoes encontradas na fase anterior para cada modelo. Sao apresentados o relatorio de classificacao completo e a matriz de confusao para cada um dos modelos. O projeto e encerrado com uma analise voltada ao contexto de negocio de credito, discutindo a diferenca de custo entre um cliente incorretamente classificado como inadimplente e um cliente inadimplente que nao foi identificado pelo modelo, e concluindo qual dos dois modelos deve ser recomendado para uso em producao.

Requisitos Tecnicos

Para a execucao do notebook, sao necessarias as seguintes bibliotecas de Python.

pandas
numpy
matplotlib
seaborn
scikit-learn
imbalanced-learn

A instalacao pode ser realizada por meio do comando abaixo.

pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn

Instrucoes de Execucao

Para executar o projeto corretamente, siga os passos abaixo.

Primeiro, posicione o arquivo credit_risk_dataset.csv na mesma pasta do notebook credit_risk_project.ipynb.

Segundo, abra o notebook em um ambiente compativel, como Jupyter Notebook, Jupyter Lab, Visual Studio Code ou Google Colab.

Terceiro, execute todas as celulas do notebook em ordem, do inicio ao fim, preferencialmente reiniciando o kernel antes da execucao completa. Este cuidado evita inconsistencias provenientes de execucoes anteriores e garante que os resultados exibidos correspondam exatamente ao codigo apresentado.

Resultados Obtidos

Ao final da Fase 6, os dois modelos selecionados apresentaram os seguintes resultados sobre o conjunto de teste, na classificacao da classe correspondente a inadimplencia.

O modelo KNN, com sete vizinhos considerados, obteve acuracia geral de oitenta e tres por cento, precisao de cinquenta e nove por cento e sensibilidade de setenta e seis por cento para a classe de inadimplencia.

O modelo de Arvore de Decisao, com profundidade maxima de cinco niveis, obteve acuracia geral de oitenta e nove por cento, precisao de setenta e quatro por cento e sensibilidade de setenta e sete por cento para a classe de inadimplencia.

Os dois modelos apresentam capacidade semelhante de identificar clientes que de fato deixam de pagar o emprestimo. No entanto, o modelo de Arvore de Decisao comete significativamente menos erros ao classificar um cliente como inadimplente quando este, na verdade, e um bom pagador. Por essa razao, a Arvore de Decisao com profundidade maxima de cinco niveis e o modelo recomendado para uso em producao, por oferecer um nivel de protecao equivalente contra o principal risco financeiro do negocio, com um impacto consideravelmente menor sobre clientes que efetivamente honram seus compromissos.

Consideracoes Finais

Todas as decisoes tecnicas adotadas ao longo do projeto, incluindo a escolha da tecnica de imputacao, o tratamento de valores discrepantes, a tecnica de balanceamento de classes e o criterio de selecao do modelo final, estao acompanhadas de justificativa textual dentro do proprio notebook, de modo a tornar o processo de decisao transparente e auditavel.

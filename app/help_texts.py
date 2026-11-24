"""Conteúdo textual exibido na janela de ajuda."""

TEXTO_AJUDA = [
    ("Sobre o programa", [
        ("p", "O programa auxilia no rebalanceamento de uma carteira de investimentos, calculando "
            "como distribuir aportes entre diferentes grupos de ativos para aproximar a carteira das "
            "porcentagens ideais definidas por você. Para facilitar o preenchimento, permite copiar "
            "diretamente de planilhas do Excel ou Google Sheets os nomes dos grupos, suas porcentagens "
            "ideais e os valores atuais da carteira. Também permite simular um rebalanceamento com "
            "vendas, caso essa opção seja habilitada, indicando os valores que seriam aportados ou "
            "vendidos em cada grupo, sem executar operações financeiras."),
    ]),
    ("Segurança e privacidade", [
        ("p", "O programa foi desenvolvido para funcionar localmente no computador do usuário. "
            "Todos os cálculos e processamentos são realizados na própria máquina, sem a necessidade "
            "de enviar os dados da carteira para servidores externos."),
        ("i", "Os dados informados no programa não são enviados ao desenvolvedor nem compartilhados "
            "com terceiros pelo funcionamento normal do aplicativo."),
        ("i", "O programa não acessa contas de corretoras, bancos ou plataformas de investimento, "
            "nem realiza operações financeiras."),
        ("i", "O programa não solicita senhas, dados bancários ou informações de acesso a contas "
            "de investimento."),
        ("i", "Mantenha o programa atualizado e faça o download apenas de fontes oficiais, como o "
            "repositório do projeto no GitHub."),
        ("i", "A segurança dos arquivos e do próprio computador também depende dos cuidados do usuário. "
            "Evite compartilhar arquivos que contenham informações financeiras pessoais.")
    ]),
        ("Grupos de ativos", [
            ("i", "Informe o nome de cada grupo de ativos ou ativos individuais, colocando um grupo por linha."),
            ("i", "Os nomes são definidos livremente por você."),
            ("i", "A ordem dos grupos deve ser a mesma em todos os campos de preenchimento."),
        ]),
    ("Porcentagem ideal", [
        ("i", "Defina o percentual desejado para cada grupo de ativos."),
        ("i", "A soma de todas as porcentagens deve ser igual a 100%."),
        ("i", "É possível informar valores como `20` ou `20%`."),
    ]),
    ("Valor atual", [
        ("i", "Informe o valor que você possui atualmente em cada grupo de ativos."),
        ("i", "Os valores devem corresponder à mesma ordem dos grupos cadastrados."),
        ("i", "Utilize a vírgula para separar as casas decimais, quando necessário. "
            "O símbolo R$ e os pontos para separar milhares são opcionais."),
        ("i", "Exemplos válidos: 1234,56 | 1.234,56 | R$ 1.234,56."),
    ]),
    ("Aporte disponível", [
        ("i", "Informe o valor total disponível para novos investimentos."),
        ("i", "O programa distribuirá esse valor entre os grupos de ativos, priorizando aqueles que "
              "estiverem abaixo da alocação ideal."),
    ]),
    ("Permitir vendas", [
        ("i", "Quando habilitada, essa opção considera a possibilidade de vender ativos de grupos que "
            "estejam acima da alocação ideal, de acordo com o desvio para venda configurado, e "
            "calcula os valores que seriam vendidos em cada grupo."),
        ("i", "Quando desabilitada, o rebalanceamento é calculado sem considerar vendas, utilizando "
            "somente o aporte disponível."),
    ]),
    ("Desvio para venda", [
        ("i", "Define o limite de desvio percentual utilizado como critério para permitir vendas de ativos."),
        ("i", "Evita que pequenas diferenças em relação à alocação ideal provoquem vendas desnecessárias."),
        ("i", "Esse parâmetro só é utilizado quando a opção \"Permitir vendas\" está habilitada."),
    ]),
    ("Botão Calcular", [
        ("p", "Realiza o rebalanceamento da carteira considerando os valores atuais, as porcentagens "
              "ideais, o aporte disponível e as regras de venda configuradas. Apresenta os valores que "
              "deverão ser aportados ou vendidos em cada grupo."),
    ]),
    ("Botão Ideal", [
        ("p", "Calcula a distribuição ideal da carteira com base nas porcentagens definidas por você, "
              "permitindo visualizar quanto cada grupo deveria possuir para atingir a alocação desejada. "
              "Nesse modo não há vendas: o resultado mostra quanto aportar em cada grupo (e o valor total "
              "da carteira) para atingir exatamente os percentuais ideais."),
    ]),
    ("Interpretando os resultados", [
        ("i", ("Valor atual:", " valor que você possui naquele grupo antes do rebalanceamento.")),
        ("i", ("Valor ideal:", " valor que o grupo deveria possuir após o rebalanceamento.")),
        ("i", ("Aporte:", " valor que deverá ser investido no grupo. Valores negativos representam "
                          "vendas de ativos.")),
        ("i", ("Desvio:", " diferença percentual entre o valor do grupo e seu objetivo após o "
                            "rebalanceamento. Desvio positivo (verde) = acima do ideal; desvio negativo "
                            "(vermelho) = abaixo do ideal.")),
        ("i", ("Gráfico de rosca:", " representação visual da distribuição da carteira entre os grupos "
                                    "de ativos.")),
    ]),
]

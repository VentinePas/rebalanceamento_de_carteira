"""Funções matemáticas para simulação do rebalanceamento da carteira."""

import math

def rebalancear(valores, pesos, orcamento):
    """
    Calcula a distribuição de um aporte entre os grupos da carteira,
    buscando aproximar seus valores da alocação ideal sem ultrapassar
    o orçamento disponível.
    """
    total_atual = sum(valores)
    total_final = total_atual + orcamento
    if total_final <= 0:
        raise ValueError("O valor total da carteira, após o aporte, precisa ser maior que zero.")

    ideais = [peso * total_final for peso in pesos]

    # Busca o maior alpha para o qual a soma dos aportes não exceda o orçamento.
    baixo, alto = 0.0, 1.0
    for _ in range(100):
        alpha = (baixo + alto) / 2
        aportes_teste = [
            max(0.0, alpha * ideal - atual)
            for atual, ideal in zip(valores, ideais)
        ]
        if sum(aportes_teste) > orcamento:
            alto = alpha
        else:
            baixo = alpha

    alpha = (baixo + alto) / 2
    aportes = [
        round(max(0.0, alpha * ideal - atual), 2)
        for atual, ideal in zip(valores, ideais)
    ]

    # Ajusta possíveis centavos de diferença do arredondamento.
    diferenca = round(orcamento - sum(aportes), 2)
    elegiveis = [i for i, aporte in enumerate(aportes) if aporte > 0]
    if elegiveis:
        indice = elegiveis[-1]
        if aportes[indice] + diferenca >= 0:
            aportes[indice] = round(aportes[indice] + diferenca, 2)

    return ideais, aportes

def calcular_vendas(valores, pesos, orcamento, desvio_max):
    """
    Calcula quanto vender de cada ativo que está acima do ideal por mais que
    desvio_max (fração, ex.: 0.15 para 15%). Vende até o ativo ficar
    exatamente no limite ideal * (1 + desvio_max).
    """
    total_final = sum(valores) + orcamento
    ideais = [peso * total_final for peso in pesos]

    vendas = []
    for atual, ideal in zip(valores, ideais):
        limite = ideal * (1 + desvio_max)
        excesso = atual - limite
        if excesso > 0.005:
            # Arredonda para cima nos centavos para nunca ficar acima do limite.
            vendas.append(math.ceil(excesso * 100 - 1e-9) / 100)
        else:
            vendas.append(0.0)
    return ideais, vendas

def rebalancear_com_vendas(valores, pesos, orcamento, desvio_max):
    """
    Retorna (ideais, movimentos, total_vendido).
    movimentos: positivo = compra, negativo = venda (valor líquido por ativo).
    """
    _, vendas = calcular_vendas(valores, pesos, orcamento, desvio_max)
    total_vendido = round(sum(vendas), 2)

    # Valores após as vendas e orçamento ampliado com o dinheiro arrecadado.
    valores_pos_venda = [atual - venda for atual, venda in zip(valores, vendas)]
    ideais, compras = rebalancear(valores_pos_venda, pesos, orcamento + total_vendido)

    movimentos = [round(compra - venda, 2) for compra, venda in zip(compras, vendas)]
    return ideais, movimentos, total_vendido

def rebalanceamento_ideal(valores, pesos):
    """
    Calcula o valor total desejado da carteira e os aportes necessários
    para atingir a alocação ideal, considerando apenas aportes e sem vendas.
    """
    if sum(valores) <= 0:
        raise ValueError(
            "O modo 'ideal' precisa de uma carteira com valor atual maior que zero. "
            "Sem um valor inicial, não há como determinar o tamanho desejado da carteira."
        )

    total_ideal = max(atual / peso for atual, peso in zip(valores, pesos))
    ideais = [peso * total_ideal for peso in pesos]
    aportes = [round(max(0.0, ideal - atual), 2) for atual, ideal in zip(valores, ideais)]

    # Mantém o aporte total consistente com o valor-alvo, até os centavos.
    aporte_alvo = round(total_ideal - sum(valores), 2)
    diferenca = round(aporte_alvo - sum(aportes), 2)
    elegiveis = [i for i, aporte in enumerate(aportes) if aporte > 0]
    if elegiveis:
        indice = elegiveis[-1]
        if aportes[indice] + diferenca >= 0:
            aportes[indice] = round(aportes[indice] + diferenca, 2)

    return total_ideal, ideais, aportes

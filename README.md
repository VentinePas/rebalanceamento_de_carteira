
# Rebalanceamento de Carteira

Aplicativo desenvolvido em Python para auxiliar no planejamento de aportes e no rebalanceamento de carteiras de investimentos.

**Versão:** 2.0.0

## Como executar

1. Certifique-se de ter Python 3 e Tkinter instalados.
2. Abra um terminal nesta pasta (a pasta que contém `main.py`).
3. Execute:

   ```bash
   python3 main.py
   ```

## Estrutura

- `main.py`: inicialização da aplicação.
- `app/gui.py`: janela principal e ações da interface.
- `app/widgets.py`: componentes reutilizáveis.
- `app/help_texts.py`: conteúdo da janela de ajuda.
- `app/theme.py`: cores e identidade visual.
- `core/calculations.py`: funções matemáticas do rebalanceamento.
- `core/formatting.py`: conversão e formatação de números.

Os arquivos `__init__.py` identificam `app` e `core` como pacotes Python.

As configurações do programa são salvas localmente no computador do usuário.

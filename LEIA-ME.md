# Criar o instalador do Rebalanceamento de Carteira para Windows

O arquivo que será enviado ao usuário final é:

`Instalador_Rebalanceamento_Carteira.exe`

Depois de instalado, o usuário pode abrir o programa pelo menu Iniciar e, opcionalmente, por um atalho na área de trabalho. Não precisa instalar Python nem usar o Prompt de Comando.

## Opção A — compilar em um computador com Windows

1. Instale o Python 3: https://www.python.org/downloads/windows/
2. Instale o Inno Setup: https://jrsoftware.org/isdl.php
3. Extraia todos os arquivos deste pacote para a mesma pasta.
4. Dê dois cliques em `gerar_instalador_windows.bat`.
5. Quando terminar, envie o arquivo `installer/Instalador_Rebalanceamento_Carteira.exe`.

Python e Inno Setup são necessários somente no computador que cria o instalador, não no computador da pessoa que vai usar o programa.

## Opção B — criar o instalador usando GitHub Actions (sem computador Windows próprio)

O pacote inclui o arquivo `.github/workflows/build-windows-installer.yml`, que compila o aplicativo em um ambiente Windows temporário do GitHub.

1. Crie um repositório no GitHub (pode ser privado para não tornar seu código público).
2. Envie para esse repositório `rebalanceamento_carteira_gui.py`, `instalador_rebalanceamento.iss` e o arquivo `.github/workflows/build-windows-installer.yml`, preservando o caminho `.github/workflows/`.
3. Abra a aba **Actions** do repositório.
4. Selecione **Criar instalador do Windows** e clique em **Run workflow**.
5. Quando a execução terminar com sucesso, abra a execução e baixe o artefato `Instalador-RebalanceamentoCarteira-Windows`.
6. Extraia o ZIP do artefato; dentro estará `Instalador_Rebalanceamento_Carteira.exe`, pronto para enviar.

## Observações

- O instalador é para Windows. O Linux precisa de uma compilação separada.
- O instalador cria um atalho no menu Iniciar e oferece a opção de criar um atalho na área de trabalho.
- O programa salva os dados do usuário no AppData do Windows e na pasta de configuração do usuário no Linux.
- No primeiro download, o Windows SmartScreen ou o serviço de e-mail pode exibir avisos por o programa ainda não ter uma assinatura digital/reputação. Isso não deve ser ignorado sem verificar que o arquivo veio de uma fonte confiável.

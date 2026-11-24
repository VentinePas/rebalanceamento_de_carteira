"""Janela principal e fluxo de interação do aplicativo."""

import json
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

from app.help_texts import TEXTO_AJUDA
from app.theme import CORES_GRAFICO, TEMA
from app.widgets import Painel, TabelaResultado, criar_icone, escolher_familia
from core.calculations import (
    rebalancear,
    rebalancear_com_vendas,
    rebalanceamento_ideal,
)
from core.formatting import (
    converter_numero_br,
    converter_percentual,
    formatar_percentual,
    moeda,
)


class AplicacaoRebalanceamento:

    def __init__(self, root):
        """
        Inicializa a aplicação, configura a janela e carrega as configurações
        salvas. Cria e organiza todos os elementos da interface gráfica,
        incluindo campos de entrada, cartões de resumo, botões, gráfico e tabela.
        """
        self.root = root
        self.root.title("Rebalanceamento de Carteira")
        self.root.configure(bg=TEMA["fundo"])
        largura = min(1320, self.root.winfo_screenwidth() - 60)
        altura = min(1000, self.root.winfo_screenheight() - 60)
        self.root.geometry(f"{largura}x{altura}")
        self.root.minsize(1100, 640)

        self.familia = escolher_familia(root)
        self.configurar_estilo()

        # Os campos são guardados na configuração do usuário e recuperados ao abrir o app.
        pasta_config = os.path.join(os.path.expanduser("~"), ".config", "rebalanceamento_carteira_aporte_gui")
        self.caminho_config = os.path.join(pasta_config, "config_rebalanceamento.json")
        self.configuracao = self.carregar_configuracao()
        self._save_after_id = None

        fundo, painel, fonte = TEMA["fundo"], TEMA["painel"], self.familia

        principal = tk.Frame(root, bg=fundo)
        principal.pack(fill="both", expand=True, padx=18, pady=14)

        # ---------- Cabeçalho ----------
        cabecalho = tk.Frame(principal, bg=fundo)
        cabecalho.pack(fill="x")
        criar_icone(cabecalho, "logo", 52).pack(side="left", padx=(4, 14))
        titulos = tk.Frame(cabecalho, bg=fundo)
        titulos.pack(side="left")
        tk.Label(titulos, text="Rebalanceamento de Carteira", bg=fundo, fg=TEMA["texto"],
                 font=(fonte, 20, "bold")).pack(anchor="w")
        tk.Label(titulos, text="Organize seus investimentos e planeje seus aportes", bg=fundo,
                 fg=TEMA["suave"], font=(fonte, 11)).pack(anchor="w")

        ttk.Button(cabecalho, text="?", width=3, style="Ajuda.Secundario.TButton", cursor="hand2",
                   command=self.abrir_ajuda).pack(side="right", padx=(0, 4))
        
        # ---------- Cartões de resumo ----------
        self.titulo_atual_var = tk.StringVar(value="Patrimônio atual")
        self.titulo_aporte_var = tk.StringVar(value="Aporte disponível")
        self.titulo_final_var = tk.StringVar(value="Patrimônio pós-aporte")
        self.valor_atual_var = tk.StringVar(value="—")
        self.valor_aporte_var = tk.StringVar(value="—")
        self.valor_final_var = tk.StringVar(value="—")

        cartoes = tk.Frame(principal, bg=fundo)
        cartoes.pack(fill="x", pady=(14, 0))
        for coluna in range(3):
            cartoes.columnconfigure(coluna, weight=1, uniform="cartao")
        self.criar_cartao(cartoes, 0, "carteira", self.titulo_atual_var, self.valor_atual_var,
                          TEMA["cartao"], TEMA["borda"])
        self.criar_cartao(cartoes, 1, "mais", self.titulo_aporte_var, self.valor_aporte_var,
                          TEMA["cartao_aporte"], TEMA["borda_aporte"])
        self.criar_cartao(cartoes, 2, "ok", self.titulo_final_var, self.valor_final_var,
                          TEMA["cartao"], TEMA["borda"])

        # ---------- Entradas ----------
        painel_entrada = Painel(principal, painel, TEMA["borda"])
        painel_entrada.pack(fill="x", pady=(14, 0))
        entrada = painel_entrada.corpo

        campos = tk.Frame(entrada, bg=painel)
        campos.pack(fill="x")
        for coluna in range(3):
            campos.columnconfigure(coluna, weight=1, uniform="coluna")

        self.grupos_texto = self.criar_campo(
            campos,
            0,
            "Grupos de Ativos",
            self.configuracao.get(
                "grupos",
                "Renda Fixa\nFundo Imobiliário\nAções\nFIIs Estrangeiro\nAções Estrangeiro\nRenda Fixa Estrangeiro\nGold\nCrypto",
            ),
            "☰",
        )
        self.percentuais_texto = self.criar_campo(
            campos,
            1,
            "Porcentagem Ideal (%)",
            self.configuracao.get("percentuais", "20\n20\n20\n6\n12\n6\n6\n10"),
            "%",
        )
        self.valores_texto = self.criar_campo(
            campos,
            2,
            "Valor Atual (R$)",
            self.configuracao.get(
                "valores",
                "985,72\n841,99\n1.043,76\n214,66\n415,96\n314,06\n208,59\n389,43",
            ),
            "R$",
        )

        # Salva automaticamente quando qualquer um dos três campos é editado.
        for campo in (self.grupos_texto, self.percentuais_texto, self.valores_texto):
            campo.edit_modified(False)
            campo.bind("<<Modified>>", self.ao_modificar_texto)

        linha_aporte = tk.Frame(entrada, bg=painel)
        linha_aporte.pack(fill="x", pady=(14, 0))
        tk.Label(linha_aporte, text="Aporte disponível (R$):", bg=painel, fg=TEMA["rotulo"],
                 font=(fonte, 10)).pack(side="left")
        self.aporte_var = tk.StringVar(value="500")
        self.aporte_entrada = ttk.Entry(linha_aporte, textvariable=self.aporte_var, width=16,
                                        style="Escuro.TEntry", font=(fonte, 10))
        self.aporte_entrada.pack(side="left", padx=(10, 14))
        self.aporte_entrada.bind("<Return>", lambda _evento: self.calcular())

        ttk.Button(linha_aporte, text="▶  Calcular", style="Primario.TButton", cursor="hand2",
                   command=self.calcular).pack(side="left", padx=(0, 10))
        tk.Frame(linha_aporte, bg=TEMA["borda"], width=1, height=26).pack(side="left", padx=(0, 10))
        ttk.Button(linha_aporte, text="Ideal", style="Secundario.TButton", cursor="hand2",
                   command=self.calcular_ideal).pack(side="left", padx=(0, 10))
        ttk.Button(linha_aporte, text="Limpar resultado", style="Secundario.TButton", cursor="hand2",
                   command=self.limpar_resultado).pack(side="left")

        linha_vendas = tk.Frame(entrada, bg=painel)
        linha_vendas.pack(fill="x", pady=(10, 0))
        self.vender_var = tk.BooleanVar(value=True)
        self.check_vender = ttk.Checkbutton(
            linha_vendas,
            text="Permitir vendas",
            variable=self.vender_var,
            command=self.alternar_vendas,
            style="Escuro.TCheckbutton",
            cursor="hand2",
        )
        self.check_vender.pack(side="left")
        tk.Label(linha_vendas, text="Desvio para venda (%):", bg=painel, fg=TEMA["rotulo"],
                 font=(fonte, 10)).pack(side="left", padx=(24, 10))
        self.desvio_venda_var = tk.StringVar(value="15")
        self.desvio_venda_entrada = ttk.Entry(
            linha_vendas,
            textvariable=self.desvio_venda_var,
            width=8,
            style="Escuro.TEntry",
            font=(fonte, 10),
            state="enable",
        )
        self.desvio_venda_entrada.pack(side="left")

        # ---------- Rodapé (empacotado antes do resultado para nunca ser cortado) ----------
        rodape = Painel(principal, painel, TEMA["borda"], raio=14, margem=12)
        rodape.pack(side="bottom", fill="x", pady=(14, 0))
        criar_icone(rodape.corpo, "info", 26).pack(side="left", padx=(0, 12))
        tk.Label(
            rodape.corpo, text="Desvio positivo = acima do ideal\nDesvio negativo = abaixo do ideal",
            bg=painel, fg=TEMA["suave"], font=(fonte, 9), justify="right", anchor="e",
        ).pack(side="right", padx=(16, 0))
        self.detalhes_resultado_var = tk.StringVar(value="")
        tk.Label(
            rodape.corpo, textvariable=self.detalhes_resultado_var, bg=painel, fg=TEMA["rotulo"],
            font=(fonte, 9), justify="left", anchor="w", wraplength=880, height=3,
        ).pack(side="left")

        # ---------- Resultado ----------
        painel_resultado = Painel(principal, painel, TEMA["borda"], expandir=True)
        painel_resultado.pack(fill="both", expand=True, pady=(14, 0))
        resultado = painel_resultado.corpo

        titulo = tk.Frame(resultado, bg=painel)
        titulo.pack(fill="x", pady=(0, 10))
        criar_icone(titulo, "logo", 24).pack(side="left", padx=(0, 8))
        tk.Label(titulo, text="Resultado", bg=painel, fg=TEMA["texto"],
                 font=(fonte, 13, "bold")).pack(side="left")
        self.modo_var = tk.StringVar(value="")
        tk.Label(titulo, textvariable=self.modo_var, bg=painel, fg=TEMA["suave"],
                 font=(fonte, 10)).pack(side="right")

        area = tk.Frame(resultado, bg=painel)
        area.pack(fill="both", expand=True)

        # O gráfico tem espaço próprio e fixo à esquerda: a tabela nunca invade essa área.
        self.grafico = tk.Canvas(area, width=480, height=270, bg=painel, highlightthickness=0, bd=0)
        self.grafico.pack(side="left", anchor="w", padx=(0, 14))

        self.resultado = TabelaResultado(area, fonte)
        self.resultado.pack(side="left", fill="both", expand=True)

        # Garante o salvamento final ao fechar a janela.
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def configurar_estilo(self):
        """Define o tema escuro dos widgets ttk (campos, botões, caixa de seleção e barras de rolagem)."""
        estilo = ttk.Style(self.root)
        estilo.theme_use("clam")

        # Botão de ajuda "?": variação compacta do botão secundário.
        estilo.configure("Ajuda.Secundario.TButton", padding=(0, 4), font=(self.familia, 11, "bold"))

        estilo.configure(
            "Escuro.TEntry",
            fieldbackground=TEMA["campo"], foreground=TEMA["texto"], insertcolor=TEMA["texto"],
            bordercolor=TEMA["campo_borda"], lightcolor=TEMA["campo_borda"], darkcolor=TEMA["campo_borda"],
            padding=(8, 6),
        )
        estilo.map(
            "Escuro.TEntry",
            fieldbackground=[("disabled", "#0A2036")],
            foreground=[("disabled", "#5F7A94")],
            bordercolor=[("focus", TEMA["azul_claro"])],
            lightcolor=[("focus", TEMA["azul_claro"])],
            darkcolor=[("focus", TEMA["azul_claro"])],
        )

        # nome: (fundo, borda, fundo ao passar o mouse, fundo ao clicar, cor do texto)
        botoes = {
            "Primario": (TEMA["azul"], TEMA["azul"], TEMA["azul_claro"], TEMA["azul_escuro"], "#FFFFFF"),
            "Secundario": (TEMA["cabecalho"], "#25598C", "#1B4B7C", "#0F2B4C", TEMA["texto"]),
        }
        for nome, (base, borda, hover, clique, texto) in botoes.items():
            estilo.configure(
                f"{nome}.TButton",
                background=base, foreground=texto, bordercolor=borda,
                lightcolor=base, darkcolor=base, focuscolor=base,
                relief="flat", padding=(18, 8), font=(self.familia, 10, "bold"),
            )
            estilo.map(
                f"{nome}.TButton",
                background=[("pressed", clique), ("active", hover)],
                lightcolor=[("pressed", clique), ("active", hover)],
                darkcolor=[("pressed", clique), ("active", hover)],
            )

        estilo.configure(
            "Escuro.TCheckbutton",
            background=TEMA["painel"], foreground=TEMA["texto"], focuscolor=TEMA["painel"],
            indicatorbackground=TEMA["campo"], indicatorforeground="#FFFFFF",
            upperbordercolor=TEMA["campo_borda"], lowerbordercolor=TEMA["campo_borda"],
            font=(self.familia, 10),
        )
        estilo.map(
            "Escuro.TCheckbutton",
            background=[("active", TEMA["painel"])],
            indicatorbackground=[("selected", TEMA["azul"]), ("active", "#0C2A47")],
        )

        estilo.configure(
            "Vertical.TScrollbar",
            background=TEMA["campo_borda"], troughcolor=TEMA["campo"], bordercolor=TEMA["campo"],
            lightcolor=TEMA["campo_borda"], darkcolor=TEMA["campo_borda"], arrowcolor=TEMA["suave"],
            gripcount=0, relief="flat",
        )
        estilo.map("Vertical.TScrollbar", background=[("active", "#2A5A88")])

    def criar_cartao(self, pai, coluna, icone, titulo_var, valor_var, fundo, borda):
        """
        Cria um cartão de resumo na parte superior da janela.

        Recebe os textos do título e do valor por variáveis que podem ser
        atualizadas posteriormente, além das cores e do ícone do cartão.
        """
        cartao = Painel(pai, fundo, borda, raio=14, margem=14)
        cartao.grid(row=0, column=coluna, sticky="ew",
                    padx=(0 if coluna == 0 else 7, 0 if coluna == 2 else 7))
        criar_icone(cartao.corpo, icone, 44).pack(side="left", padx=(0, 14))
        textos = tk.Frame(cartao.corpo, bg=fundo)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(textos, textvariable=titulo_var, bg=fundo, fg=TEMA["suave"],
                 font=(self.familia, 10), anchor="w").pack(fill="x")
        tk.Label(textos, textvariable=valor_var, bg=fundo, fg=TEMA["texto"],
                 font=(self.familia, 19, "bold"), anchor="w").pack(fill="x")
        return cartao

    def atualizar_cartoes(self, atual, aporte, final, titulo_aporte="Aporte disponível"):
        """Atualiza os três cartões do topo; None mostra um traço."""
        self.titulo_aporte_var.set(titulo_aporte)
        for variavel, valor in (
            (self.valor_atual_var, atual),
            (self.valor_aporte_var, aporte),
            (self.valor_final_var, final),
        ):
            variavel.set("—" if valor is None else moeda(valor))

    def abrir_ajuda(self):
        """Abre a janela de ajuda (apenas uma por vez)."""
        janela = getattr(self, "_janela_ajuda", None)
        if janela is not None and janela.winfo_exists():
            janela.deiconify()
            janela.lift()
            janela.focus_force()
            return

        fonte, fundo, painel = self.familia, TEMA["fundo"], TEMA["painel"]
        janela = tk.Toplevel(self.root)
        self._janela_ajuda = janela
        janela.title("Ajuda — Rebalanceamento de Carteira")
        janela.configure(bg=fundo)
        janela.transient(self.root)

        # Centraliza sobre a janela principal, sem sair da tela.
        self.root.update_idletasks()
        largura = min(780, self.root.winfo_screenwidth() - 80)
        altura = min(700, self.root.winfo_screenheight() - 120)
        x = self.root.winfo_rootx() + (self.root.winfo_width() - largura) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - altura) // 2
        x = max(0, min(x, self.root.winfo_screenwidth() - largura))
        y = max(0, min(y, self.root.winfo_screenheight() - altura))
        janela.geometry(f"{largura}x{altura}+{x}+{y}")
        janela.minsize(520, 380)

        def fechar(_evento=None):
            self._janela_ajuda = None
            janela.destroy()

        janela.protocol("WM_DELETE_WINDOW", fechar)
        janela.bind("<Escape>", fechar)

        corpo = tk.Frame(janela, bg=fundo)
        corpo.pack(fill="both", expand=True, padx=18, pady=14)

        cabecalho = tk.Frame(corpo, bg=fundo)
        cabecalho.pack(fill="x")
        criar_icone(cabecalho, "info", 34).pack(side="left", padx=(2, 12))
        titulos = tk.Frame(cabecalho, bg=fundo)
        titulos.pack(side="left")
        tk.Label(titulos, text="Como usar o programa", bg=fundo, fg=TEMA["texto"],
                 font=(fonte, 16, "bold")).pack(anchor="w")
        tk.Label(titulos, text="Guia rápido para preencher os campos e interpretar o resultado",
                 bg=fundo, fg=TEMA["suave"], font=(fonte, 10)).pack(anchor="w")

        # Rodapé empacotado antes do painel para nunca ser cortado.
        rodape = tk.Frame(corpo, bg=fundo)
        rodape.pack(side="bottom", fill="x", pady=(12, 0))
        ttk.Button(rodape, text="Fechar", style="Secundario.TButton", cursor="hand2",
                   command=fechar).pack(side="right")

        quadro = Painel(corpo, painel, TEMA["borda"], expandir=True)
        quadro.pack(fill="both", expand=True, pady=(12, 0))

        texto = tk.Text(
            quadro.corpo, wrap="word", bg=painel, fg=TEMA["texto"], relief="flat", bd=0,
            highlightthickness=0, padx=10, pady=6, cursor="arrow", takefocus=0,
            selectbackground="#245B94", selectforeground="#FFFFFF", font=(fonte, 10),
        )
        barra = ttk.Scrollbar(quadro.corpo, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        texto.pack(side="left", fill="both", expand=True)

        # Estilos do texto (os últimos criados têm prioridade sobre os anteriores).
        recuo = tkfont.Font(family=fonte, size=10).measure("•  ")
        texto.tag_configure("secao", font=(fonte, 12, "bold"), foreground=TEMA["azul_claro"],
                            spacing1=6, spacing3=6)
        texto.tag_configure("texto", font=(fonte, 10), foreground=TEMA["texto"], spacing3=6)
        texto.tag_configure("item", font=(fonte, 10), foreground=TEMA["texto"],
                            lmargin1=10, lmargin2=10 + recuo, spacing3=4)
        texto.tag_configure("divisor", font=(fonte, 1), background=TEMA["borda"],
                            spacing1=10, spacing3=10)
        texto.tag_configure("negrito", font=(fonte, 10, "bold"))
        texto.tag_configure("codigo", font=(fonte, 10, "bold"), foreground=TEMA["verde"])

        def escrever(trecho, tag):
            """
            Insere um trecho de texto no widget, aplicando a formatação indicada
            pela tag. Partes delimitadas por crases (`) recebem também a formatação
            de código, para destacar exemplos e comandos.
            """
            for i, parte in enumerate(trecho.split("`")):
                if parte:
                    texto.insert("end", parte, (tag, "codigo") if i % 2 else (tag,))

        for n, (titulo_secao, blocos) in enumerate(TEXTO_AJUDA):
            texto.insert("end", titulo_secao + "\n", "secao")
            for tipo, conteudo in blocos:
                if tipo == "p":
                    escrever(conteudo, "texto")
                    texto.insert("end", "\n", "texto")
                else:
                    texto.insert("end", "•  ", "item")
                    if isinstance(conteudo, tuple):
                        texto.insert("end", conteudo[0], ("item", "negrito"))
                        conteudo = conteudo[1]
                    escrever(conteudo, "item")
                    texto.insert("end", "\n", "item")
            if n < len(TEXTO_AJUDA) - 1:
                texto.insert("end", "\n", "divisor")

        texto.configure(state="disabled")  # somente leitura
        janela.focus_set()

    def alternar_vendas(self):
        """
        Habilita ou desabilita o campo de desvio para venda conforme
        o estado da opção "Permitir vendas".
        """
        if self.vender_var.get():
            self.desvio_venda_entrada.config(state="normal")
        else:
            self.desvio_venda_entrada.config(state="disabled")

    def carregar_configuracao(self):
        """Carrega os campos salvos; se não houver arquivo, usa os valores padrão."""
        try:
            with open(self.caminho_config, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (OSError, json.JSONDecodeError):
            return {}

        if not isinstance(dados, dict):
            return {}

        # Só aceita texto para evitar que um arquivo de configuração inválido quebre a janela.
        return {
            chave: dados[chave]
            for chave in ("grupos", "percentuais", "valores")
            if isinstance(dados.get(chave), str)
        }

    def salvar_configuracao(self, mostrar_erro=False):
        """Persiste os três campos em JSON, usando arquivo temporário para evitar gravação parcial."""
        self._save_after_id = None
        dados = {
            "grupos": self.grupos_texto.get("1.0", "end-1c"),
            "percentuais": self.percentuais_texto.get("1.0", "end-1c"),
            "valores": self.valores_texto.get("1.0", "end-1c"),
        }
        arquivo_temporario = self.caminho_config + ".tmp"

        try:
            os.makedirs(os.path.dirname(self.caminho_config), exist_ok=True)
            with open(arquivo_temporario, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            os.replace(arquivo_temporario, self.caminho_config)
            return True
        except OSError as erro:
            try:
                if os.path.exists(arquivo_temporario):
                    os.remove(arquivo_temporario)
            except OSError:
                pass
            if mostrar_erro:
                messagebox.showerror(
                    "Erro ao salvar dados",
                    f"Não foi possível salvar os campos preenchidos.\n\n{erro}",
                    parent=self.root,
                )
            return False

    def ao_modificar_texto(self, evento):
        """Agenda o salvamento após uma breve pausa na digitação."""
        campo = evento.widget
        if not campo.edit_modified():
            return

        campo.edit_modified(False)
        if self._save_after_id is not None:
            self.root.after_cancel(self._save_after_id)
        self._save_after_id = self.root.after(400, self.salvar_configuracao)

    def ao_fechar(self):
        """Salva imediatamente antes de encerrar o programa."""
        if self._save_after_id is not None:
            self.root.after_cancel(self._save_after_id)
            self._save_after_id = None
        self.salvar_configuracao(mostrar_erro=True)
        self.root.destroy()

    def criar_campo(self, pai, coluna, titulo, conteudo_inicial, icone):
        """
        Cria um campo de texto com título, ícone e barra de rolagem.

        Posiciona o campo na coluna indicada, preenche-o com o conteúdo
        inicial e retorna o widget de texto para permitir sua utilização
        e edição por outras partes do programa.
        """
        quadro = tk.Frame(pai, bg=TEMA["painel"])
        quadro.grid(row=0, column=coluna, sticky="nsew",
                    padx=(0 if coluna == 0 else 8, 0 if coluna == 2 else 8))
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(1, weight=1)

        cabecalho = tk.Frame(quadro, bg=TEMA["painel"])
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        tk.Label(cabecalho, text=icone, bg=TEMA["painel"], fg=TEMA["azul_claro"],
                 font=(self.familia, 13, "bold")).pack(side="left", padx=(2, 8))
        tk.Label(cabecalho, text=titulo, bg=TEMA["painel"], fg=TEMA["texto"],
                 font=(self.familia, 11, "bold")).pack(side="left")

        texto = tk.Text(
            quadro, height=8, width=10, wrap="word", undo=True,
            bg=TEMA["campo"], fg=TEMA["texto"], insertbackground=TEMA["texto"],
            selectbackground="#245B94", selectforeground="#FFFFFF",
            relief="flat", bd=0, padx=10, pady=8, font=(self.familia, 10),
            highlightthickness=1, highlightbackground=TEMA["campo_borda"], highlightcolor=TEMA["azul_claro"],
        )
        barra = ttk.Scrollbar(quadro, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        texto.grid(row=1, column=0, sticky="nsew")
        barra.grid(row=1, column=1, sticky="ns", padx=(4, 0))
        texto.insert("1.0", conteudo_inicial)
        texto.edit_modified(False)
        return texto
    
    @staticmethod
    def linhas_validas(widget):
        """
        Lê o conteúdo de um campo de texto e retorna apenas as linhas
        que possuem algum conteúdo, removendo espaços extras no início e no fim.
        """
        return [linha.strip() for linha in widget.get("1.0", "end-1c").splitlines() if linha.strip()]

    @staticmethod
    def _cortar_texto(texto, fonte, largura_max):
        """Encurta o texto com reticências para caber na largura (em pixels)."""
        if fonte.measure(texto) <= largura_max:
            return texto
        while texto and fonte.measure(texto + "…") > largura_max:
            texto = texto[:-1]
        return texto + "…"

    def atualizar_grafico(self, nomes, valores):
        """Mostra o gráfico de rosca com os valores finais do resultado."""
        c = self.grafico
        c.delete("all")
        total = sum(valores)
        if not nomes or total <= 0:
            return

        fundo = TEMA["painel"]
        largura, altura = int(c["width"]), int(c["height"])
        cx, cy, raio, espessura = 104, altura // 2, 92, 32
        raio_arco = raio - espessura / 2
        bbox = (cx - raio_arco, cy - raio_arco, cx + raio_arco, cy + raio_arco)

        # Fatias (começam no topo e seguem no sentido horário).
        inicio, acumulado, angulos_divisa = 90.0, 0.0, []
        for i, valor in enumerate(valores):
            if valor <= 0:
                continue
            varredura = 360 * valor / total
            c.create_arc(
                bbox, start=inicio, extent=-min(varredura, 359.99),
                style="arc", width=espessura,
                outline=CORES_GRAFICO[i % len(CORES_GRAFICO)],
            )
            inicio -= varredura
            acumulado += varredura
            angulos_divisa.append(acumulado)

        # Pequenas divisórias entre as fatias.
        if len(angulos_divisa) > 1:
            for ang in angulos_divisa:
                rad = math.radians(ang)
                c.create_line(
                    cx + (raio - espessura) * math.sin(rad), cy - (raio - espessura) * math.cos(rad),
                    cx + raio * math.sin(rad), cy - raio * math.cos(rad),
                    fill=fundo, width=2,
                )

        # Texto central (a fonte diminui se o total for muito grande).
        texto_total = moeda(total)
        tamanho = 13
        while tamanho > 8 and tkfont.Font(
            family=self.familia, size=tamanho, weight="bold"
        ).measure(texto_total) > 2 * (raio - espessura) - 14:
            tamanho -= 1
        c.create_text(cx, cy - 9, text=texto_total, fill=TEMA["texto"],
                      font=(self.familia, tamanho, "bold"))
        c.create_text(cx, cy + 12, text="Total", fill=TEMA["suave"], font=(self.familia, 10))

        # Legenda à direita.
        fonte = tkfont.Font(family=self.familia, size=10)
        x_ponto, x_nome, x_pct = 226, 244, largura - 12
        largura_nome = x_pct - 54 - x_nome
        n = len(nomes)
        passo = min(28, (altura - 24) / n)
        y = (altura - passo * (n - 1)) / 2
        for i, (nome, valor) in enumerate(zip(nomes, valores)):
            cor = CORES_GRAFICO[i % len(CORES_GRAFICO)]
            c.create_oval(x_ponto - 6, y - 6, x_ponto + 6, y + 6, fill=cor, outline=cor)
            c.create_text(x_nome, y, text=self._cortar_texto(nome, fonte, largura_nome), anchor="w",
                          fill=TEMA["texto"], font=(self.familia, 10))
            c.create_text(x_pct, y, text=formatar_percentual(valor / total), anchor="e",
                          fill=TEMA["texto"], font=(self.familia, 10))
            y += passo

    def limpar_resultado(self):
        """
        Limpa os resultados exibidos na interface, incluindo a tabela,
        o gráfico, as informações adicionais e os cartões de resumo,
        retornando a área de resultados ao estado inicial.
        """
        self.resultado.limpar()
        self.modo_var.set("")
        self.detalhes_resultado_var.set("")
        self.grafico.delete("all")
        self.atualizar_cartoes(None, None, None)

    def preencher_tabela(self, nomes, valores, ideais, aportes, mostrar_desvio=False):
        """Preenche a tabela de resultado (desvio colorido) e a linha de totais."""
        linhas = []
        for nome, atual, ideal, aporte in zip(nomes, valores, ideais, aportes):
            texto_desvio, cor_desvio = "", TEMA["texto"]
            if mostrar_desvio:
                desvio = -(ideal - atual - aporte) / ideal if ideal else 0.0
                if abs(desvio) < 0.0005:
                    desvio = 0.0
                texto_desvio = formatar_percentual(desvio)
                if desvio > 0:
                    cor_desvio = TEMA["verde"]      # abaixo do ideal
                elif desvio < 0:
                    cor_desvio = TEMA["vermelho"]   # acima do ideal
            linhas.append([
                (nome, TEMA["texto"]),
                (moeda(atual), TEMA["texto"]),
                (moeda(ideal), TEMA["texto"]),
                (moeda(aporte), TEMA["texto"]),
                (texto_desvio, cor_desvio),
            ])

        total = [
            "TOTAL",
            moeda(sum(valores)),
            moeda(sum(ideais)),
            moeda(sum(aportes)),
            "—" if mostrar_desvio else "",
        ]
        self.resultado.preencher(linhas, total)
        
    def calcular_ideal(self):
        """
        Lê e valida os dados informados, calcula os aportes necessários para
        atingir a distribuição ideal da carteira sem realizar vendas e atualiza
        os cartões de resumo, a tabela, o gráfico e as informações do resultado.

        Exibe uma mensagem de erro caso os dados sejam inválidos ou o cálculo
        não possa ser realizado.
        """
        try:
            nomes = self.linhas_validas(self.grupos_texto)
            percentuais_linhas = self.linhas_validas(self.percentuais_texto)
            valores_linhas = self.linhas_validas(self.valores_texto)

            if not nomes:
                raise ValueError("Informe pelo menos um grupo de ativos.")
            if not (len(nomes) == len(percentuais_linhas) == len(valores_linhas)):
                raise ValueError(
                    "A quantidade de linhas precisa ser igual nos três campos: "
                    "grupo, porcentagem ideal e valor atual."
                )

            percentuais = [converter_percentual(valor) for valor in percentuais_linhas]
            valores = [converter_numero_br(valor) for valor in valores_linhas]

            if any(p <= 0 or p > 100 for p in percentuais):
                raise ValueError(
                    "Cada porcentagem ideal precisa ser maior que 0 e menor ou igual a 100. "
                    "O modo 'ideal' não funciona com grupos de peso zero."
                )
            soma_percentuais = sum(percentuais)
            if abs(soma_percentuais - 100.0) > 0.05:
                raise ValueError(
                    f"A soma das porcentagens ideais deve ser 100%. "
                    f"A soma informada foi {soma_percentuais:.2f}%."
                )

            if any(valor < 0 for valor in valores):
                raise ValueError("Os valores atuais não podem ser negativos.")

            # Normaliza diferenças muito pequenas decorrentes de arredondamento.
            pesos = [(percentual / soma_percentuais) for percentual in percentuais]
            
            
            total_ideal, ideais, aportes = rebalanceamento_ideal(valores, pesos)
            aporte_total = sum(aportes)
            total_pos_aporte = sum(valores) + aporte_total

            self.modo_var.set("Modo: rebalanceamento ideal")
            self.atualizar_cartoes(sum(valores), aporte_total, total_pos_aporte, "Aporte necessário")

            self.preencher_tabela(nomes, valores, ideais, aportes)
            self.atualizar_grafico(nomes, [a + b for a, b in zip(valores, aportes)])
            self.detalhes_resultado_var.set(
                f"Aporte total: {moeda(aporte_total)}    |    "
                f"Valor final da carteira: {moeda(total_pos_aporte)}\n"
                "Observação: o modo 'ideal' não vende ativos; calcula os aportes necessários "
                "para alcançar os pesos desejados aumentando a carteira até o valor-alvo compatível."
            )

        except (ValueError, ZeroDivisionError) as erro:
            messagebox.showerror("Não foi possível calcular", str(erro), parent=self.root)

    def calcular(self):
        """
        Lê e valida os dados da carteira e o orçamento disponível.
        Calcula como distribuir o aporte entre os grupos, com ou sem vendas,
        conforme a opção selecionada.

        Atualiza os cartões de resumo, a tabela, o gráfico e as informações
        do resultado. Exibe uma mensagem caso os dados sejam inválidos
        ou o cálculo não possa ser realizado.
        """
        try:
            nomes = self.linhas_validas(self.grupos_texto)
            percentuais_linhas = self.linhas_validas(self.percentuais_texto)
            valores_linhas = self.linhas_validas(self.valores_texto)

            if not nomes:
                raise ValueError("Informe pelo menos um grupo de ativos.")
            if not (len(nomes) == len(percentuais_linhas) == len(valores_linhas)):
                raise ValueError(
                    "A quantidade de linhas precisa ser igual nos três campos: "
                    "grupo, porcentagem ideal e valor atual."
                )

            percentuais = [converter_percentual(valor) for valor in percentuais_linhas]
            valores = [converter_numero_br(valor) for valor in valores_linhas]

            if any(p <= 0 or p > 100 for p in percentuais):
                raise ValueError(
                    "Cada porcentagem ideal precisa ser maior que 0 e menor ou igual a 100. "
                    "O modo 'ideal' não funciona com grupos de peso zero."
                )
            soma_percentuais = sum(percentuais)
            if abs(soma_percentuais - 100.0) > 0.05:
                raise ValueError(
                    f"A soma das porcentagens ideais deve ser 100%. "
                    f"A soma informada foi {soma_percentuais:.2f}%."
                )

            if any(valor < 0 for valor in valores):
                raise ValueError("Os valores atuais não podem ser negativos.")

            # Normaliza diferenças muito pequenas decorrentes de arredondamento.
            pesos = [(percentual / soma_percentuais) for percentual in percentuais]
            entrada_orcamento = self.aporte_var.get().strip()

            orcamento = converter_numero_br(entrada_orcamento)
            if orcamento < 0:
                raise ValueError("O aporte disponível não pode ser negativo.")

            total_vendido = 0.0
            if self.vender_var.get():
                desvio_max = converter_percentual(self.desvio_venda_var.get()) / 100
                if desvio_max < 0:
                    raise ValueError("O desvio para venda não pode ser negativo.")
                ideais, aportes, total_vendido = rebalancear_com_vendas(
                    valores, pesos, orcamento, desvio_max
                )
            else:
                ideais, aportes = rebalancear(valores, pesos, orcamento)

            total_atual = sum(valores)
            total_final = total_atual + sum(aportes)
            total_comprado = sum(a for a in aportes if a > 0)

            self.modo_var.set("Modo: orçamento limitado" + (" com vendas" if self.vender_var.get() else ""))
            self.atualizar_cartoes(total_atual, orcamento, total_final)
            
            self.preencher_tabela(nomes, valores, ideais, aportes, mostrar_desvio=True)
            self.atualizar_grafico(nomes, [a + b for a, b in zip(valores, aportes)])
            
            if self.vender_var.get():
                detalhes = (
                    f"Total comprado: {moeda(total_comprado)}    |    "
                    f"Total vendido: {moeda(total_vendido)}\n"
                    "Valores negativos na coluna Aporte são vendas. "
                )
            else:
                detalhes = f"Aporte total distribuído: {moeda(sum(aportes))}\n"
            self.detalhes_resultado_var.set(
                detalhes
                + "O desvio indica a diferença relativa entre o valor ideal e o valor após o aporte."
            )

        except (ValueError, ZeroDivisionError) as erro:
            messagebox.showerror("Não foi possível calcular", str(erro), parent=self.root)

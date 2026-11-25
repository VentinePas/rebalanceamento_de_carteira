"""Componentes reutilizáveis da interface Tkinter."""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from app.theme import TEMA


def escala(widget):
    """Fator de escala da tela em relação a 96 DPI (1.0 = 100%, 1.5 = 150%...).

    As fontes são dadas em pontos e já acompanham a escala do Tk. Este fator serve para
    que as medidas dadas em pixels (ícones, margens, gráfico) acompanhem as fontes.
    """
    return max(1.0, widget.winfo_fpixels("1i") / 96.0)


def escolher_familia(root):
    """Escolhe a primeira fonte moderna disponível no sistema."""
    disponiveis = set(tkfont.families(root))
    for nome in ("Segoe UI", "Ubuntu", "Noto Sans", "DejaVu Sans", "Helvetica"):
        if nome in disponiveis:
            return nome
    return tkfont.nametofont("TkDefaultFont").actual("family")

def criar_icone(pai, tipo, tamanho=44):
    """Desenha pequenos ícones em um Canvas (não dependem de imagens nem de fontes)."""
    tamanho = int(tamanho * escala(pai))
    c = tk.Canvas(pai, width=tamanho, height=tamanho, bg=pai.cget("bg"), highlightthickness=0, bd=0)
    k = tamanho / 48.0
    traco = max(2.0, 4 * k)

    def p(*valores):
        return [v * k for v in valores]

    if tipo == "logo":
        c.create_rectangle(*p(6, 34, 16, 44), fill=TEMA["verde"], outline="")
        c.create_rectangle(*p(19, 26, 29, 44), fill=TEMA["verde"], outline="")
        c.create_rectangle(*p(32, 17, 42, 44), fill=TEMA["verde"], outline="")
        c.create_line(*p(6, 22, 17, 12, 26, 18, 40, 5), fill=TEMA["verde"], width=traco,
                      arrow="last", arrowshape=(8 * k, 10 * k, 4 * k), joinstyle="round")
    elif tipo == "carteira":
        c.create_rectangle(*p(4, 10, 40, 40), fill=TEMA["azul_claro"], outline="")
        c.create_rectangle(*p(4, 10, 40, 16), fill="#7DB7F7", outline="")
        c.create_rectangle(*p(28, 22, 44, 32), fill=TEMA["azul_escuro"], outline="")
        c.create_oval(*p(32, 25, 38, 31), fill="#CFE5FC", outline="")
    elif tipo == "mais":
        c.create_oval(*p(2, 2, 46, 46), fill=TEMA["verde"], outline="")
        c.create_line(*p(24, 13, 24, 35), fill="#FFFFFF", width=traco, capstyle="round")
        c.create_line(*p(13, 24, 35, 24), fill="#FFFFFF", width=traco, capstyle="round")
    elif tipo == "ok":
        c.create_oval(*p(2, 2, 46, 46), fill=TEMA["azul_claro"], outline="")
        c.create_line(*p(14, 25, 21, 32, 34, 17), fill="#FFFFFF", width=traco,
                      capstyle="round", joinstyle="round")
    else:  # "info"
        c.create_oval(*p(2, 2, 46, 46), fill=TEMA["azul_claro"], outline="")
        c.create_line(*p(24, 21, 24, 35), fill="#FFFFFF", width=traco, capstyle="round")
        c.create_oval(*p(21.5, 11, 26.5, 16), fill="#FFFFFF", outline="")
    return c

class Painel(tk.Canvas):
    """Painel com cantos arredondados. Crie os widgets dentro de `painel.corpo`.

    O painel sempre pede ao gerenciador de geometria o tamanho que o conteúdo precisa
    (o seu tamanho mínimo). Com expandir=True o conteúdo também acompanha o painel quando
    ele recebe mais espaço; com expandir=False o conteúdo mantém a sua altura natural.
    """

    def __init__(self, pai, fundo, borda, raio=16, margem=14, expandir=False):
        super().__init__(pai, width=10, height=10, bg=pai.cget("bg"), highlightthickness=0, bd=0)
        esc = escala(pai)
        self._fundo, self._borda = fundo, borda
        self._raio, self._margem, self._expandir = int(raio * esc), int(margem * esc), expandir
        self.corpo = tk.Frame(self, bg=fundo)
        self._janela = self.create_window(self._margem, self._margem, anchor="nw", window=self.corpo)
        self.bind("<Configure>", self._redesenhar)
        # O tamanho pedido é medido uma vez depois que a janela é montada
        # e de novo sempre que o conteúdo mudar de tamanho.
        self.corpo.bind("<Configure>", self._ajustar_tamanho)
        self.after(20, self.medir)

    def medir(self):
        """Atualiza o tamanho que o painel pede ao gerenciador de geometria."""
        self.corpo.update_idletasks()
        self._ajustar_tamanho()

    def _ajustar_tamanho(self, _evento=None):
        largura = self.corpo.winfo_reqwidth() + 2 * self._margem
        altura = self.corpo.winfo_reqheight() + 2 * self._margem
        if int(self.cget("width")) != largura or int(self.cget("height")) != altura:
            self.configure(width=largura, height=altura)

    def _redesenhar(self, evento):
        x1 = y1 = 1
        x2, y2 = evento.width - 2, evento.height - 2
        r = max(0, min(self._raio, (x2 - x1) // 2, (y2 - y1) // 2))
        pontos = [
            x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
            x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
            x1, y1 + r, x1, y1,
        ]
        self.delete("fundo")
        self.create_polygon(pontos, smooth=True, fill=self._fundo, outline=self._borda, tags="fundo")
        self.tag_lower("fundo")

        largura = max(1, evento.width - 2 * self._margem)
        if self._expandir:
            self.itemconfigure(self._janela, width=largura, height=max(1, evento.height - 2 * self._margem))
        else:
            self.itemconfigure(self._janela, width=largura)

class TabelaResultado(tk.Frame):
    """Tabela feita com Labels: cada célula pode ter cor própria e as colunas se ajustam ao conteúdo."""

    TITULOS = ("Grupo de Ativos", "Valor atual (R$)", "Valor ideal (R$)", "Aporte (R$)", "Desvio")
    ANCORAS = ("w", "e", "e", "e", "e")
    PESOS = (3, 2, 2, 2, 1)  # como o espaço que sobra é dividido entre as colunas

    def __init__(self, pai, familia):
        super().__init__(pai, bg=TEMA["painel"])
        self.familia = familia
        # altura aproximada de uma linha (texto + pady + borda), para o tamanho mínimo da tabela
        self._altura_linha = tkfont.Font(self, family=familia, size=10).metrics("linespace") + 12
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, width=10, height=10, bg=TEMA["painel"], highlightthickness=0, bd=0)
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.barra.grid(row=0, column=1, sticky="ns")

        self.interno = tk.Frame(self.canvas, bg=TEMA["painel"])
        self._janela = self.canvas.create_window(0, 0, anchor="nw", window=self.interno)
        for coluna, peso in enumerate(self.PESOS):
            self.interno.columnconfigure(coluna, weight=peso)

        self.interno.bind("<Configure>", self._ao_mudar_conteudo)
        self.canvas.bind("<Configure>", self._ao_mudar_canvas)
        self._vincular_rolagem(self.canvas)
        self._vincular_rolagem(self.interno)

        self.limpar()

    # ----- rolagem -----
    def medir(self):
        """Atualiza o tamanho pedido pela tabela (força a medição sem esperar eventos)."""
        self.interno.update_idletasks()
        self._ao_mudar_conteudo()

    def _ao_mudar_conteudo(self, _evento=None):
        # A tabela pede a largura que as colunas precisam (nada de texto cortado) e uma
        # altura mínima de cabeçalho + 3 linhas; acima disso, rola por dentro.
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"),
            width=self.interno.winfo_reqwidth(),
            height=min(self.interno.winfo_reqheight(), 4 * self._altura_linha),
        )
        self._atualizar_barra()

    def _ao_mudar_canvas(self, evento):
        self.canvas.itemconfigure(self._janela, width=evento.width)
        self._atualizar_barra()

    def _atualizar_barra(self):
        """Mostra a barra de rolagem só quando as linhas não cabem."""
        if self.interno.winfo_reqheight() > self.canvas.winfo_height():
            self.barra.grid()
        else:
            self.barra.grid_remove()
            self.canvas.yview_moveto(0)

    def _vincular_rolagem(self, widget):
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(evento, self._rolar)

    def _rolar(self, evento):
        if not self.barra.winfo_ismapped():
            return
        direcao = -1 if (evento.num == 4 or evento.delta > 0) else 1
        self.canvas.yview_scroll(direcao * 2, "units")

    # ----- conteúdo -----
    def _celula(self, linha, coluna, texto, fundo, cor=None, negrito=False):
        rotulo = tk.Label(
            self.interno, text=texto, bg=fundo, fg=cor or TEMA["texto"],
            anchor=self.ANCORAS[coluna], padx=14, pady=5,
            font=(self.familia, 10, "bold" if negrito else "normal"),
        )
        rotulo.grid(row=linha, column=coluna, sticky="nsew")
        self._vincular_rolagem(rotulo)

    def _resetar(self):
        for filho in self.interno.winfo_children():
            filho.destroy()
        for coluna, titulo in enumerate(self.TITULOS):
            self._celula(0, coluna, titulo, TEMA["cabecalho"], negrito=True)
        self.canvas.yview_moveto(0)

    def limpar(self, mensagem="Preencha os campos e clique em Calcular para ver o resultado."):
        self._resetar()
        aviso = tk.Label(
            self.interno, text=mensagem, bg=TEMA["linha_par"], fg=TEMA["suave"],
            font=(self.familia, 10), pady=18,
        )
        aviso.grid(row=1, column=0, columnspan=len(self.TITULOS), sticky="nsew")

    def preencher(self, linhas, total):
        """linhas: lista de linhas, cada uma com 5 pares (texto, cor); total: lista de 5 textos."""
        self._resetar()
        for i, linha in enumerate(linhas, start=1):
            fundo = TEMA["linha_par"] if i % 2 else TEMA["linha_impar"]
            for coluna, (texto, cor) in enumerate(linha):
                self._celula(i, coluna, texto, fundo, cor)
        for coluna, texto in enumerate(total):
            self._celula(len(linhas) + 1, coluna, texto, TEMA["total"], negrito=True)

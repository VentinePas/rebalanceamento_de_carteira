import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


def converter_numero_br(texto):
    """Converte números no formato brasileiro (ex.: 1.234,56) para float."""
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if not texto:
        raise ValueError("Há um valor vazio.")

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1:
        texto = texto.replace(".", "")
    elif "." in texto:
        parte_decimal = texto.rsplit(".", 1)[1]
        # Sem vírgula, um ponto seguido de três dígitos é tratado como milhar.
        if len(parte_decimal) == 3:
            texto = texto.replace(".", "")

    return float(texto)


def converter_percentual(texto):
    """Recebe 20, 20% ou 20,5% e retorna o percentual como número."""
    texto = texto.strip().replace("%", "").replace(" ", "")
    if not texto:
        raise ValueError("Há um percentual vazio.")
    return float(texto.replace(",", "."))


def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def rebalancear(valores, pesos, orcamento):
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


def rebalanceamento_ideal(valores, pesos):
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


class AplicacaoRebalanceamento:
    def __init__(self, root):
        self.root = root
        self.root.title("Rebalanceamento de Carteira")
        self.root.geometry("1100x760")
        self.root.minsize(850, 650)

        # Os campos são guardados na configuração do usuário e recuperados ao abrir o app.
        pasta_config = os.path.join(os.path.expanduser("~"), ".config", "rebalanceamento_carteira_gui")
        self.caminho_config = os.path.join(pasta_config, "config.json")
        self.configuracao = self.carregar_configuracao()
        self._save_after_id = None

        principal = ttk.Frame(root, padding=14)
        principal.pack(fill="both", expand=True)

        ttk.Label(
            principal,
            text="Rebalanceamento de carteira",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        ttk.Label(
            principal,
            text=(
                "Preencha uma linha por grupo. Use percentuais como 20 ou 20%. "
                "Nos valores, pode usar por exemplo 1.234,56."
            ),
            wraplength=1000,
        ).pack(anchor="w", pady=(0, 12))

        campos = ttk.Frame(principal)
        campos.pack(fill="both", expand=True)
        for coluna in range(3):
            campos.columnconfigure(coluna, weight=1, uniform="coluna")
        campos.rowconfigure(0, weight=1)

        self.grupos_texto = self.criar_campo(
            campos,
            0,
            "Grupo de Ativos",
            self.configuracao.get(
                "grupos",
                "Renda Fixa\nFundo Imobiliário\nAções\nFIIs Estrangeiro\nAções Estrangeiro\nRenda Fixa Estrangeiro\nGold\nCrypto",
            ),
        )
        self.percentuais_texto = self.criar_campo(
            campos,
            1,
            "Porcentagem Ideal (%)",
            self.configuracao.get("percentuais", "20\n20\n20\n6\n12\n6\n6\n10"),
        )
        self.valores_texto = self.criar_campo(
            campos,
            2,
            "Valor Atual (R$)",
            self.configuracao.get(
                "valores",
                "985,72\n841,99\n1.043,76\n214,66\n415,96\n314,06\n208,59\n389,43",
            ),
        )

        # Salva automaticamente quando qualquer um dos três campos é editado.
        for campo in (self.grupos_texto, self.percentuais_texto, self.valores_texto):
            campo.edit_modified(False)
            campo.bind("<<Modified>>", self.ao_modificar_texto)

        linha_aporte = ttk.Frame(principal)
        linha_aporte.pack(fill="x", pady=(12, 8))
        ttk.Label(linha_aporte, text="Aporte disponível (R$ ou 'ideal'):").pack(side="left")
        self.aporte_var = tk.StringVar(value="500")
        self.aporte_entrada = ttk.Entry(linha_aporte, textvariable=self.aporte_var, width=18)
        self.aporte_entrada.pack(side="left", padx=(8, 12))
        self.aporte_entrada.bind("<Return>", lambda _evento: self.calcular())

        ttk.Button(linha_aporte, text="Calcular", command=self.calcular).pack(side="left", padx=(0, 8))
        ttk.Button(linha_aporte, text="Limpar resultado", command=self.limpar_resultado).pack(side="left")

        ttk.Label(principal, text="Resultado:", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(6, 4))
        quadro_resultado = ttk.Frame(principal)
        quadro_resultado.pack(fill="both", expand=True)

        self.resumo_var = tk.StringVar(value="Preencha os campos e clique em Calcular para ver o resultado.")
        ttk.Label(
            quadro_resultado,
            textvariable=self.resumo_var,
            justify="left",
            anchor="w",
            wraplength=1000,
        ).pack(fill="x", anchor="w", pady=(0, 6))

        moldura_tabela = ttk.Frame(quadro_resultado)
        moldura_tabela.pack(fill="both", expand=True)
        moldura_tabela.rowconfigure(0, weight=1)
        moldura_tabela.columnconfigure(0, weight=1)

        colunas = ("grupo", "atual", "ideal", "aporte", "desvio")
        self.resultado = ttk.Treeview(
            moldura_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )
        titulos = {
            "grupo": "Grupo de Ativos",
            "atual": "Valor atual (R$)",
            "ideal": "Valor ideal (R$)",
            "aporte": "Aporte (R$)",
            "desvio": "Desvio",
        }
        for coluna in colunas:
            self.resultado.heading(coluna, text=titulos[coluna])

        self.resultado.column("grupo", width=220, minwidth=150, anchor="w", stretch=True)
        self.resultado.column("atual", width=135, minwidth=115, anchor="e", stretch=False)
        self.resultado.column("ideal", width=135, minwidth=115, anchor="e", stretch=False)
        self.resultado.column("aporte", width=135, minwidth=115, anchor="e", stretch=False)
        self.resultado.column("desvio", width=85, minwidth=75, anchor="e", stretch=False)

        # Cores alternadas deixam cada ativo mais fácil de acompanhar horizontalmente.
        self.resultado.tag_configure("linha_par", background="#FFFFFF")
        self.resultado.tag_configure("linha_impar", background="#F0F4F8")
        self.resultado.tag_configure(
            "total",
            background="#DCE5EF",
            font=("TkDefaultFont", 10, "bold"),
        )
        estilo_tabela = ttk.Style()
        estilo_tabela.configure("Treeview", rowheight=25, font=("TkDefaultFont", 10))
        estilo_tabela.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"))

        barra_vertical = ttk.Scrollbar(moldura_tabela, orient="vertical", command=self.resultado.yview)
        barra_horizontal = ttk.Scrollbar(moldura_tabela, orient="horizontal", command=self.resultado.xview)
        self.resultado.configure(yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set)
        self.resultado.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")

        self.detalhes_resultado_var = tk.StringVar(value="")
        ttk.Label(
            quadro_resultado,
            textvariable=self.detalhes_resultado_var,
            justify="left",
            anchor="w",
            wraplength=1000,
        ).pack(fill="x", anchor="w", pady=(6, 0))

        # Garante o salvamento final ao fechar a janela.
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

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

    def criar_campo(self, pai, coluna, titulo, conteudo_inicial):
        quadro = ttk.LabelFrame(pai, text=titulo, padding=6)
        quadro.grid(row=0, column=coluna, sticky="nsew", padx=(0 if coluna == 0 else 6, 0))
        quadro.rowconfigure(0, weight=1)
        quadro.columnconfigure(0, weight=1)

        texto = tk.Text(quadro, height=7, width=28, wrap="word", undo=True)
        barra = ttk.Scrollbar(quadro, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        texto.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        texto.insert("1.0", conteudo_inicial)
        texto.edit_modified(False)
        return texto

    @staticmethod
    def linhas_validas(widget):
        return [linha.strip() for linha in widget.get("1.0", "end-1c").splitlines() if linha.strip()]

    def limpar_resultado(self):
        for item in self.resultado.get_children():
            self.resultado.delete(item)
        self.resumo_var.set("Preencha os campos e clique em Calcular para ver o resultado.")
        self.detalhes_resultado_var.set("")

    def preencher_tabela(self, nomes, valores, ideais, aportes, mostrar_desvio=False):
        """Preenche a tabela com valores alinhados e uma linha de totais."""
        for item in self.resultado.get_children():
            self.resultado.delete(item)

        for indice, (nome, atual, ideal, aporte) in enumerate(zip(nomes, valores, ideais, aportes)):
            if mostrar_desvio:
                desvio = (ideal - atual - aporte) / ideal if ideal else 0.0
                texto_desvio = f"{desvio:.1%}"
            else:
                texto_desvio = ""

            tag = "linha_par" if indice % 2 == 0 else "linha_impar"
            self.resultado.insert(
                "",
                "end",
                values=(nome, moeda(atual), moeda(ideal), moeda(aporte), texto_desvio),
                tags=(tag,),
            )

        self.resultado.insert(
            "",
            "end",
            values=(
                "TOTAL",
                moeda(sum(valores)),
                moeda(sum(ideais)),
                moeda(sum(aportes)),
                "—" if mostrar_desvio else "",
            ),
            tags=("total",),
        )

    def calcular(self):
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

            if entrada_orcamento.lower() == "ideal":
                total_ideal, ideais, aportes = rebalanceamento_ideal(valores, pesos)
                aporte_total = sum(aportes)
                total_pos_aporte = sum(valores) + aporte_total

                self.resumo_var.set(
                    f"Modo: rebalanceamento ideal    |    "
                    f"Valor atual da carteira: {moeda(sum(valores))}    |    "
                    f"Valor-alvo da carteira: {moeda(total_ideal)}"
                )
                self.preencher_tabela(nomes, valores, ideais, aportes)
                self.detalhes_resultado_var.set(
                    f"Aporte total: {moeda(aporte_total)}    |    "
                    f"Valor final da carteira: {moeda(total_pos_aporte)}\n"
                    "Observação: o modo 'ideal' não vende ativos; calcula os aportes necessários "
                    "para alcançar os pesos desejados aumentando a carteira até o valor-alvo compatível."
                )
            else:
                orcamento = converter_numero_br(entrada_orcamento)
                if orcamento < 0:
                    raise ValueError("O aporte disponível não pode ser negativo.")

                ideais, aportes = rebalancear(valores, pesos, orcamento)
                total_atual = sum(valores)
                total_final = total_atual + sum(aportes)

                self.resumo_var.set(
                    f"Modo: orçamento limitado    |    "
                    f"Valor atual da carteira: {moeda(total_atual)}    |    "
                    f"Orçamento disponível: {moeda(orcamento)}    |    "
                    f"Valor final da carteira: {moeda(total_final)}"
                )
                self.preencher_tabela(nomes, valores, ideais, aportes, mostrar_desvio=True)
                self.detalhes_resultado_var.set(
                    f"Aporte total distribuído: {moeda(sum(aportes))}\n"
                    "O desvio indica a diferença relativa entre o valor ideal e o valor após o aporte. "
                    "Desvio positivo = abaixo do ideal; desvio negativo = acima do ideal."
                )

        except (ValueError, ZeroDivisionError) as erro:
            messagebox.showerror("Não foi possível calcular", str(erro), parent=self.root)


def main():
    root = tk.Tk()
    AplicacaoRebalanceamento(root)
    root.mainloop()


if __name__ == "__main__":
    main()

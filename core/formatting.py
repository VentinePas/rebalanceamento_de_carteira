"""Conversão e apresentação de números no padrão brasileiro."""

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
    """
    Formata um valor numérico como moeda brasileira (R$),
    usando ponto para milhares e vírgula para decimais.
    """
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

def formatar_percentual(valor):
    """Formata uma fração no padrão brasileiro (ex.: 0.05 -> 5,0%)."""
    return f"{valor:.1%}".replace(".", ",")

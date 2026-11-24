"""Ponto de entrada do Rebalanceamento de Carteira."""

import tkinter as tk

from app.gui import AplicacaoRebalanceamento


def main():
    root = tk.Tk()
    AplicacaoRebalanceamento(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# Tamanho da Academia comp x largura
# Lista de Maquina Comp x largura e Setor, quantidade
# Folga entre as maquinas 1x

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import csv

def importar_csv():
    caminho = filedialog.askopenfilename(
        title="Selecionar arquivo de máquinas",
        filetypes=[("CSV", "*.csv")]
    )

    if not caminho:
        return

    try:
        with open(caminho, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for linha in reader:
                maq = {
                    "nome":  linha["nome"],
                    "w":     float(linha["comp"]),
                    "h":     float(linha["larg"]),
                    "setor": int(linha["setor"])
                }
                maquinas.append(maq)
                tree.insert("", "end", values=(
                    maq["nome"], maq["w"], maq["h"], maq["setor"]
                ))

        messagebox.showinfo("Sucesso", f"{len(maquinas)} máquinas carregadas!")

    except Exception as e:
        messagebox.showerror("Erro ao ler CSV", str(e))

maquinas = []

def adicionar_maquina():
    nome = entry_nome.get().strip()
    comp = entry_comp.get().strip()
    larg = entry_larg.get().strip()
    setor = entry_setor.get().strip()
    qtd = entry_qtd.get().strip()

    try:
        comp = float(comp)
        larg = float(larg)
        setor = int(setor)
        qtd = int(qtd)

    except ValueError:
        messagebox.showerror("Erro", "Comprimento, largura, quantidade e setor devem ser números.")
        return

    if not nome:
        messagebox.showerror("Erro", "Informe o nome da máquina.")
        return

    maquinas.append({"nome": nome, "w": comp, "h": larg, "setor": setor, "qtd": qtd})

    #adiciona linha na tabela
    tree.insert("", "end", values=(nome, comp, larg, setor))

    #limpa os campos
    entry_nome.delete(0, tk.END)
    entry_comp.delete(0, tk.END)
    entry_larg.delete(0, tk.END)
    entry_setor.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)

def otimizar():
    try:
        W = float(entry_W.get())
        H = float(entry_H.get())
        folga = float(entry_folga.get())
    except ValueError:
        messagebox.showerror("Erro", "Preencha as dimensões do galpão corretamente.")
        return

    if len(maquinas) == 0:
        messagebox.showerror("Erro", "Adicione ao menos uma máquina.")
        return

    #aqui vai a chamada pro modelo.py
    print("Rodando otimização...")
    print(f"Galpão: {W}x{H}, Folga: {folga}")
    print("Máquinas:", maquinas)

root = tk.Tk()
root.title("Academia — Otimizador de Layout")
root.resizable(False, False)


main = ttk.Frame(root, padding=12)
main.pack()

### Criando os label e os inputs
ttk.LabelFrame(main, text="Dimensões do Galpão").grid(row=0, column=0, sticky="ew", pady=(0,8))
frame_galpao = ttk.LabelFrame(main, text="Dimensões do Galpão")
frame_galpao.grid(row=0, column=0, sticky="ew", pady=(0, 8))

ttk.Label(frame_galpao, text="Comprimento (m):").grid(row=0, column=0, sticky="w", padx=4)
entry_W = ttk.Entry(frame_galpao, width=10)
entry_W.grid(row=0, column=1, padx=4, pady=3)

ttk.Label(frame_galpao, text="Largura (m):").grid(row=1, column=0, sticky="w", padx=4)
entry_H = ttk.Entry(frame_galpao, width=10)
entry_H.grid(row=1, column=1, padx=4, pady=3)

frame_folga = ttk.LabelFrame(main, text="Folga entre Máquinas")
frame_folga.grid(row=1, column=0, sticky="ew", pady=(0, 8))

ttk.Label(frame_folga, text="Folga mínima (m):").grid(row=0, column=0, sticky="w", padx=4)
entry_folga = ttk.Entry(frame_folga, width=10)
entry_folga.insert(0, "1.0")
entry_folga.grid(row=0, column=1, padx=4, pady=3)

frame_add = ttk.LabelFrame(main, text="Adicionar Máquina")
frame_add.grid(row=2, column=0, sticky="ew", pady=(0,8))
ttk.Button(frame_add, text=" 📥 Importar csv", command=importar_csv).grid(row=0, column=0, columnspan=12, padx=0, pady=4)

ttk.Label(frame_add, text="Nome:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
entry_nome = ttk.Entry(frame_add, width=14)
entry_nome.grid(row=1, column=1, padx=0, pady=10)

ttk.Label(frame_add, text="Comp (m):").grid(row=1, column=2, sticky="w", padx=4)
entry_comp = ttk.Entry(frame_add, width=7)
entry_comp.grid(row=1, column=3, padx=4, pady=2)

ttk.Label(frame_add, text="Larg (m):").grid(row=1, column=4, sticky="w", padx=4)
entry_larg = ttk.Entry(frame_add, width=7)
entry_larg.grid(row=1, column=5, padx=4, pady=2)

ttk.Label(frame_add, text="Setor:").grid(row=1, column=6, sticky="w", padx=4)
entry_setor = ttk.Entry(frame_add, width=5)
entry_setor.grid(row=1, column=7, padx=4, pady=2)

ttk.Label(frame_add, text="qtd:").grid(row=1, column=8, sticky="w", padx=4)
entry_qtd = ttk.Entry(frame_add, width=2)
entry_qtd.grid(row=1, column=9, padx=4, pady=2)

ttk.Button(frame_add, text="+ Adicionar", command=adicionar_maquina).grid(row=1, column=11, padx=8)

frame_tabela = ttk.LabelFrame(main, text="Máquinas Cadastradas")
frame_tabela.grid(row=3, column=0, sticky="ew", pady=(0, 8))

cols = ("Nome", "Comp (m)", "Larg (m)", "Setor")
tree = ttk.Treeview(frame_tabela, columns=cols, show="headings", height=6)
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=100)
tree.pack(padx=4, pady=4)

ttk.Button(main, text="Gerar Layout", command=otimizar).grid(row=4, column=0, sticky="ew", pady=4)

root.mainloop()
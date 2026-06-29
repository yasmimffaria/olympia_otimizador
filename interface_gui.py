# Tamanho da Academia comp x largura
# Lista de Maquina Comp x largura e Setor, quantidade
# Folga entre as maquinas 1x

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import csv

from modelo import resolver_modelo
from visualizacao import desenhar_layout
from relatorio import gerar_relatorio

def _opt_float(valor):
    # converte texto em float; retorna None se vazio/ausente (posicao livre)
    valor = (valor or "").strip()
    return float(valor) if valor else None

def importar_csv():
    caminho = filedialog.askopenfilename(
        title="Selecionar arquivo de máquinas",
        filetypes=[("CSV", "*.csv")]
    )

    if not caminho:
        return

    try:
        # conta so o que foi carregado deste arquivo (nao a lista global)
        linhas_carregadas = 0   # numero de tipos (linhas do CSV)
        total_carregado = 0     # numero de maquinas individuais (somando qtd)

        with open(caminho, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for linha in reader:
                maq = {
                    "nome":  linha["nome"],
                    "w":     float(linha["comp"]),
                    "h":     float(linha["larg"]),
                    "setor": int(linha["setor"]),
                    "qtd":    int(linha["qtd"]),
                    # posicao fixa opcional: colunas x / y (vazias = posicao livre)
                    "x_fixo": _opt_float(linha.get("x")),
                    "y_fixo": _opt_float(linha.get("y")),
                }
                maquinas.append(maq)
                tree.insert("", "end", values=(
                    maq["nome"], maq["w"], maq["h"], maq["setor"], maq["qtd"],
                    "" if maq["x_fixo"] is None else maq["x_fixo"],
                    "" if maq["y_fixo"] is None else maq["y_fixo"]
                ))
                linhas_carregadas += 1
                total_carregado += maq["qtd"]

        messagebox.showinfo(
            "Sucesso",
            f"{linhas_carregadas} tipos carregados ({total_carregado} máquinas no total)."
        )

    except Exception as e:
        messagebox.showerror("Erro ao ler CSV", str(e))

maquinas = []
ultimo_resultado = None  # guarda o resultado do ultimo "Gerar Layout" pra exportar

def adicionar_maquina():
    nome = entry_nome.get().strip()
    comp = entry_comp.get().strip()
    larg = entry_larg.get().strip()
    setor = entry_setor.get().strip()
    qtd = entry_qtd.get().strip()
    x_txt = entry_x.get().strip()
    y_txt = entry_y.get().strip()

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

    # posicao fixa e opcional, mas X e Y precisam vir juntos
    if (x_txt == "") != (y_txt == ""):
        messagebox.showerror("Erro", "Para fixar um item, preencha X e Y juntos (ou deixe ambos vazios).")
        return
    try:
        x_fixo = float(x_txt) if x_txt else None
        y_fixo = float(y_txt) if y_txt else None
    except ValueError:
        messagebox.showerror("Erro", "X e Y devem ser números.")
        return

    maquinas.append({"nome": nome, "w": comp, "h": larg, "setor": setor, "qtd": qtd,
                     "x_fixo": x_fixo, "y_fixo": y_fixo})

    #adiciona linha na tabela
    tree.insert("", "end", values=(
        nome, comp, larg, setor, qtd,
        "" if x_fixo is None else x_fixo,
        "" if y_fixo is None else y_fixo
    ))

    #limpa os campos
    entry_nome.delete(0, tk.END)
    entry_comp.delete(0, tk.END)
    entry_larg.delete(0, tk.END)
    entry_setor.delete(0, tk.END)
    entry_qtd.delete(0, tk.END)
    entry_x.delete(0, tk.END)
    entry_y.delete(0, tk.END)

def otimizar():
    try:
        W = float(entry_W.get())
        H = float(entry_H.get())
        folga = float(entry_folga.get())
    except ValueError:
        messagebox.showerror("Erro", "Preencha as dimensões do galpão corretamente.")
        return

    # tempo limite e opcional: vazio = sem limite
    tempo_txt = entry_tempo.get().strip()
    tempo_limite = None
    if tempo_txt:
        try:
            tempo_limite = float(tempo_txt)
            if tempo_limite <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Tempo máximo deve ser um número positivo (ou vazio).")
            return

    if len(maquinas) == 0:
        messagebox.showerror("Erro", "Adicione ao menos uma máquina.")
        return

    resultado = resolver_modelo(W, H, folga, maquinas, tempo_limite=tempo_limite)

    # sem nenhuma solucao factivel pra desenhar -> nao mostra o layout
    if not resultado["tem_solucao"]:
        if resultado.get("mensagem"):
            messagebox.showwarning("Posição fixa inválida", resultado["mensagem"])
            return
        if resultado.get("sol_status") == "Infeasible":
            msg = ("O problema é inviável: não existe layout que caiba todas as "
                   "máquinas na área informada com essa folga.\n"
                   "Aumente a área do galpão ou reduza a folga / as máquinas.")
        else:
            msg = ("O solver não encontrou um layout viável no tempo disponível.\n"
                   "Tente dar mais tempo ao solver, aumentar a área ou reduzir a folga.")
        messagebox.showwarning("Sem solução factível", msg)
        return

    # achou solucao, mas pode nao ser a otima (tempo estourou)
    if resultado["status"] != "Optimal":
        messagebox.showinfo(
            "Solução parcial",
            f"O tempo limite foi atingido (status '{resultado['status']}').\n"
            "Mostrando a melhor solução encontrada até agora — pode não ser a ótima."
        )

    # guarda o ultimo resultado pra permitir exportar o relatorio depois
    global ultimo_resultado
    ultimo_resultado = resultado

    desenhar_layout(resultado)


def exportar_relatorio():
    if ultimo_resultado is None:
        messagebox.showwarning(
            "Sem resultado",
            "Gere um layout primeiro (botão 'Gerar Layout') antes de exportar o relatório."
        )
        return

    caminho = filedialog.asksaveasfilename(
        title="Salvar relatório",
        defaultextension=".html",
        initialfile="relatorio_layout.html",
        filetypes=[("HTML", "*.html")]
    )
    if not caminho:
        return

    try:
        html_path, csv_path = gerar_relatorio(ultimo_resultado, caminho)
        messagebox.showinfo(
            "Relatório gerado",
            f"Relatório salvo em:\n{html_path}\n\nDados (CSV) em:\n{csv_path}"
        )
    except Exception as e:
        messagebox.showerror("Erro ao gerar relatório", str(e))



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

frame_folga = ttk.LabelFrame(main, text="Folga e Solver")
frame_folga.grid(row=1, column=0, sticky="ew", pady=(0, 8))

ttk.Label(frame_folga, text="Folga mínima (m):").grid(row=0, column=0, sticky="w", padx=4)
entry_folga = ttk.Entry(frame_folga, width=10)
entry_folga.insert(0, "1.0")
entry_folga.grid(row=0, column=1, padx=4, pady=3)

ttk.Label(frame_folga, text="Tempo máximo (s):").grid(row=0, column=2, sticky="w", padx=4)
entry_tempo = ttk.Entry(frame_folga, width=10)
entry_tempo.insert(0, "60")
entry_tempo.grid(row=0, column=3, padx=4, pady=3)
ttk.Label(frame_folga, text="(vazio = sem limite)").grid(row=1, column=2, columnspan=2, sticky="w", padx=4)

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

# posicao fixa opcional (item vira obstaculo travado nessa coordenada)
ttk.Label(frame_add, text="X fixo (m):").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))
entry_x = ttk.Entry(frame_add, width=7)
entry_x.grid(row=2, column=1, padx=0, pady=(0, 8))

ttk.Label(frame_add, text="Y fixo (m):").grid(row=2, column=2, sticky="w", padx=4, pady=(0, 8))
entry_y = ttk.Entry(frame_add, width=7)
entry_y.grid(row=2, column=3, padx=4, pady=(0, 8))

ttk.Label(frame_add, text="(opcional — vazio = posição livre)").grid(
    row=2, column=4, columnspan=8, sticky="w", padx=4, pady=(0, 8))

frame_tabela = ttk.LabelFrame(main, text="Máquinas Cadastradas")
frame_tabela.grid(row=3, column=0, sticky="ew", pady=(0, 8))

cols = ("Nome", "Comp (m)", "Larg (m)", "Setor", "Qtd", "X fixo", "Y fixo")
tree = ttk.Treeview(frame_tabela, columns=cols, show="headings", height=6)
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=100)
# colunas de posicao fixa mais estreitas
tree.column("X fixo", width=60, anchor="center")
tree.column("Y fixo", width=60, anchor="center")
tree.pack(padx=4, pady=4)

frame_acoes = ttk.Frame(main)
frame_acoes.grid(row=4, column=0, sticky="ew", pady=4)
frame_acoes.columnconfigure(0, weight=1)
frame_acoes.columnconfigure(1, weight=1)

ttk.Button(frame_acoes, text="Gerar Layout", command=otimizar).grid(row=0, column=0, sticky="ew", padx=(0, 4))
ttk.Button(frame_acoes, text="📄 Exportar relatório (HTML + CSV)", command=exportar_relatorio).grid(row=0, column=1, sticky="ew", padx=(4, 0))

root.mainloop()
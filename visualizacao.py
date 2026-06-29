import matplotlib.pyplot as plt
import matplotlib.patches as patches


# nomes amigaveis pros setores (so pra legenda)
NOMES_SETORES = {
    1: "Costas / Peito",
    2: "Pernas",
    3: "Outras partes",
    4: "Objetos inerentes",
}

# uma cor por setor
CORES_SETORES = {
    1: "#1f77b4",  # azul
    2: "#2ca02c",  # verde
    3: "#ff7f0e",  # laranja
    4: "#7f7f7f",  # cinza
}


def desenhar_layout(resultado, salvar_em=None, mostrar=True):
    """Desenha o layout retornado por resolver_modelo usando matplotlib.

    resultado - dicionario devolvido por modelo.resolver_modelo
    salvar_em - caminho opcional pra salvar a figura (ex: 'layout.png')
    mostrar   - se True abre a janela do matplotlib
    """

    W = resultado["W"]
    H = resultado["H"]
    setores = resultado["setores"]
    maquinas = resultado["maquinas"]

    fig, ax = plt.subplots(figsize=(10, 10 * H / W if W else 10))

    # ---- contorno da academia (galpao) ----
    ax.add_patch(patches.Rectangle(
        (0, 0), W, H,
        fill=False, edgecolor="black", linewidth=2
    ))

    # ---- retangulos dos setores ----
    for i, setor_id in enumerate(setores):
        x = resultado["X_set"][i]
        y = resultado["Y_set"][i]
        larg = resultado["L_set"][i]
        alt = resultado["A_set"][i]

        cor = CORES_SETORES.get(setor_id, "#cccccc")
        ax.add_patch(patches.Rectangle(
            (x, y), larg, alt,
            fill=True, facecolor=cor, alpha=0.08,
            edgecolor=cor, linewidth=1.5, linestyle="--"
        ))

    # ---- maquinas ----
    for i, maq in enumerate(maquinas):
        x = resultado["x_maq"][i]
        y = resultado["y_maq"][i]
        w = maq["w"]
        h = maq["h"]
        cor = CORES_SETORES.get(maq["setor"], "#cccccc")

        # itens fixos (pilares, recepcao...) sao desenhados com hachura e borda grossa
        fixa = maq.get("fixa", False)
        ax.add_patch(patches.Rectangle(
            (x, y), w, h,
            fill=True, facecolor=cor, alpha=0.6,
            edgecolor="black", linewidth=2.0 if fixa else 0.7,
            hatch="xx" if fixa else None
        ))

        # nome da maquina centralizado dentro do retangulo
        ax.text(
            x + w / 2, y + h / 2, maq["nome"],
            ha="center", va="center", fontsize=5.5,
            wrap=True, color="black"
        )

    # ---- legenda dos setores ----
    handles = [
        patches.Patch(facecolor=CORES_SETORES[s], alpha=0.6,
                      label=f"{s} - {NOMES_SETORES.get(s, 'Setor ' + str(s))}")
        for s in sorted(CORES_SETORES) if s in setores
    ]
    # marca na legenda o estilo dos itens fixos, se houver algum
    if any(m.get("fixa") for m in maquinas):
        handles.append(patches.Patch(facecolor="white", edgecolor="black",
                                     linewidth=2.0, hatch="xx", label="Item fixo"))

    if handles:
        ax.legend(handles=handles, loc="upper left",
                  bbox_to_anchor=(1.01, 1.0), fontsize=8, title="Setores")

    # ---- ajustes finais ----
    ax.set_xlim(-0.5, W + 0.5)
    ax.set_ylim(-0.5, H + 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel("Comprimento (m)")
    ax.set_ylabel("Largura (m)")

    status = resultado.get("status", "?")
    larga = resultado.get("Larga_usada")
    titulo = f"Layout da Academia — status: {status}"
    if larga is not None:
        titulo += f" | largura usada: {larga:.2f} m"
    ax.set_title(titulo)

    fig.tight_layout()

    if salvar_em:
        fig.savefig(salvar_em, dpi=150, bbox_inches="tight")

    if mostrar:
        plt.show()

    return fig

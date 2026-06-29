import base64
import csv
import io
import html
from datetime import datetime

import matplotlib.pyplot as plt

from visualizacao import desenhar_layout, NOMES_SETORES


def _fig_para_base64(resultado):
    # gera a figura do layout e devolve como PNG embutivel (base64)
    fig = desenhar_layout(resultado, mostrar=False)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)  # libera a figura da memoria
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("ascii")


def _resumo(resultado):
    # numeros pro texto em linguagem natural
    maquinas = resultado["maquinas"]
    W, H = resultado["W"], resultado["H"]
    qtd = len(maquinas)
    qtd_setores = len(resultado["setores"])
    qtd_fixas = sum(1 for m in maquinas if m.get("fixa"))

    area_galpao = W * H
    area_maquinas = sum(m["w"] * m["h"] for m in maquinas)
    ocupacao = (area_maquinas / area_galpao * 100) if area_galpao else 0

    return {
        "qtd": qtd,
        "qtd_setores": qtd_setores,
        "qtd_fixas": qtd_fixas,
        "area_galpao": area_galpao,
        "area_maquinas": area_maquinas,
        "ocupacao": ocupacao,
    }


def gerar_html(resultado, caminho, titulo="Relatório de Layout — Academia"):
    """Gera um relatorio .html autocontido (imagem embutida) com os resultados."""

    r = _resumo(resultado)
    W, H = resultado["W"], resultado["H"]
    folga = resultado.get("folga")
    largura = resultado.get("Larga_usada")
    status = resultado.get("status", "?")
    otima = status == "Optimal"
    img64 = _fig_para_base64(resultado)

    e = html.escape  # encurta o escape de texto

    # ---- texto do resumo em linguagem natural ----
    aviso_status = (
        "<p class='ok'>✔ Solução ótima encontrada.</p>" if otima else
        f"<p class='warn'>⚠ Solução parcial (status do solver: {e(status)}). "
        "Pode não ser a melhor possível — rode com mais tempo se quiser tentar melhorar.</p>"
    )
    largura_txt = f"{largura:.2f} m" if largura is not None else "—"

    # ---- tabela de maquinas ----
    linhas_maq = []
    for i, m in enumerate(resultado["maquinas"]):
        x = resultado["x_maq"][i]
        y = resultado["y_maq"][i]
        linhas_maq.append(
            "<tr>"
            f"<td>{i + 1}</td>"
            f"<td>{e(m['nome'])}</td>"
            f"<td>{m['setor']}</td>"
            f"<td>{x:.2f}</td><td>{y:.2f}</td>"
            f"<td>{m['w']:.2f}</td><td>{m['h']:.2f}</td>"
            f"<td>{'Sim' if m.get('fixa') else 'Não'}</td>"
            "</tr>"
        )

    # ---- tabela de setores ----
    linhas_set = []
    for i, setor_id in enumerate(resultado["setores"]):
        nome = NOMES_SETORES.get(setor_id, f"Setor {setor_id}")
        linhas_set.append(
            "<tr>"
            f"<td>{setor_id}</td><td>{e(nome)}</td>"
            f"<td>{resultado['X_set'][i]:.2f}</td><td>{resultado['Y_set'][i]:.2f}</td>"
            f"<td>{resultado['L_set'][i]:.2f}</td><td>{resultado['A_set'][i]:.2f}</td>"
            "</tr>"
        )

    html_doc = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{e(titulo)}</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; margin: 32px; color: #222; }}
  h1 {{ color: #1f3a5f; }}
  h2 {{ color: #1f3a5f; border-bottom: 2px solid #e0e0e0; padding-bottom: 4px; margin-top: 28px; }}
  .meta {{ color: #666; font-size: 0.9em; }}
  .ok {{ color: #2ca02c; font-weight: bold; }}
  .warn {{ color: #c0392b; font-weight: bold; }}
  table {{ border-collapse: collapse; margin-top: 8px; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: center; font-size: 0.9em; }}
  th {{ background: #1f3a5f; color: white; }}
  tr:nth-child(even) td {{ background: #f4f6f8; }}
  .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }}
  .card {{ background: #f4f6f8; border: 1px solid #ddd; border-radius: 8px;
           padding: 12px 18px; min-width: 150px; }}
  .card .num {{ font-size: 1.6em; font-weight: bold; color: #1f3a5f; }}
  img {{ max-width: 100%; border: 1px solid #ccc; margin-top: 8px; }}
</style>
</head>
<body>
  <h1>{e(titulo)}</h1>
  <p class="meta">Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>

  {aviso_status}

  <h2>Resumo</h2>
  <p>Foram posicionadas <b>{r['qtd']} máquinas</b> em <b>{r['qtd_setores']} setores</b>
     dentro de um galpão de <b>{W:.2f} m × {H:.2f} m</b>
     (folga mínima entre máquinas: {folga:.2f} m).
     {r['qtd_fixas']} item(ns) com posição fixa.</p>

  <div class="cards">
    <div class="card"><div class="num">{largura_txt}</div>Largura ocupada</div>
    <div class="card"><div class="num">{r['area_maquinas']:.1f} m²</div>Área das máquinas</div>
    <div class="card"><div class="num">{r['area_galpao']:.1f} m²</div>Área do galpão</div>
    <div class="card"><div class="num">{r['ocupacao']:.1f}%</div>Ocupação</div>
  </div>

  <h2>Layout</h2>
  <img src="data:image/png;base64,{img64}" alt="Layout da academia">

  <h2>Máquinas</h2>
  <table>
    <tr><th>#</th><th>Nome</th><th>Setor</th><th>X (m)</th><th>Y (m)</th>
        <th>Comp (m)</th><th>Larg (m)</th><th>Fixa</th></tr>
    {''.join(linhas_maq)}
  </table>

  <h2>Setores</h2>
  <table>
    <tr><th>Setor</th><th>Nome</th><th>X (m)</th><th>Y (m)</th>
        <th>Largura (m)</th><th>Altura (m)</th></tr>
    {''.join(linhas_set)}
  </table>
</body>
</html>"""

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_doc)


def gerar_csv(resultado, caminho):
    """Gera um .csv com as posicoes das maquinas (dados brutos)."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nome", "setor", "x", "y", "comp", "larg", "fixa"])
        for i, m in enumerate(resultado["maquinas"]):
            writer.writerow([
                m["nome"], m["setor"],
                round(resultado["x_maq"][i], 3), round(resultado["y_maq"][i], 3),
                round(m["w"], 3), round(m["h"], 3),
                "sim" if m.get("fixa") else "nao",
            ])


def gerar_relatorio(resultado, caminho_html):
    """Gera o relatorio HTML e um CSV de mesmo nome (.csv) ao lado.

    Retorna os dois caminhos gerados.
    """
    if caminho_html.lower().endswith(".html"):
        caminho_csv = caminho_html[:-5] + ".csv"
    else:
        caminho_csv = caminho_html + ".csv"

    gerar_html(resultado, caminho_html)
    gerar_csv(resultado, caminho_csv)
    return caminho_html, caminho_csv

from pulp import *


def resolver_modelo(W, H, folga, maquinas, tempo_limite=None):
    # Resolve o modelo em si

    # W            - Largura da area da academia
    # H            - Outra dimensão da área da academia
    # folga        - espaco entre as maquinas
    # maquinas     - dicionario das maquinas
    # tempo_limite - tempo maximo em segundos pro solver (None = sem limite)

    # exemplo de maquinas:
    #   {
    #       'nome': 'esteira',
    #       'w': 1.0,
    #       'h': 2.0,
    #       'setor': 1,
    #       'qtd': 5
    #   },{
    #       'nome': 'bike',
    #       'w': 1.0,
    #       'h': 2.0,
    #       'setor': 1,
    #       'qtd': 1
    #   }


    # ============================================================
    # separa as maquinas em uma nova lista por quantidade
    # pra ter um item pra cada maquina ao inves de pra cada tipo de maquina
    maquinas_porQtd = []
    for maq in maquinas:
        for i in range(maq["qtd"]):
            maquinas_porQtd.append({
                # copia os atributos da maquina original
                "nome": maq["nome"],
                "w": maq["w"],
                "h": maq["h"],
                "setor": maq["setor"],

                # posicao fixa opcional (None = posicao livre / decidida pelo solver)
                "x_fixo": maq.get("x_fixo"),
                "y_fixo": maq.get("y_fixo"),

                # cria um id pra cada uma das maquinas
                "id": i+1
            })

    # listar os setores
    setores = list(set(maq["setor"] for maq in maquinas_porQtd))

    # pega a qtd de maquinas e de setores
    qtd_maquinas = len(maquinas_porQtd)
    qtd_setores = len(setores)

    # marca quais maquinas tem posicao fixa (sao obstaculos)
    eh_fixa = [
        maq["x_fixo"] is not None and maq["y_fixo"] is not None
        for maq in maquinas_porQtd
    ]

    # adiciona metade da folga em cada lado da maquina
    # guarda a dimensao real (sem folga) pra poder desenhar depois
    for maq in maquinas_porQtd:
        maq["w_real"] = maq["w"]
        maq["h_real"] = maq["h"]
        maq["w"] += folga / 2
        maq["h"] += folga / 2

    # ============================================================
    # Cria o problema com o pulp
    problema = LpProblem("Problema_de_disposicao_de_maquinas", LpMinimize)

    # ==========
    # Cria as variaveis de decisao

    # pos de cada maquina
    x_maq = LpVariable.dicts("x", range(qtd_maquinas), lowBound=0, upBound=W, cat="Continuous")
    y_maq = LpVariable.dicts("y", range(qtd_maquinas), lowBound=0, upBound=H, cat="Continuous")
    
    # pos de cada setor
    X_set = LpVariable.dicts("X", range(qtd_setores), lowBound=0, upBound=W, cat="Continuous")
    Y_set = LpVariable.dicts("Y", range(qtd_setores), lowBound=0, upBound=H, cat="Continuous")

    # altura e largura de cada setor
    A_set = LpVariable.dicts("A", range(qtd_setores), lowBound=0, upBound=W, cat="Continuous")
    L_set = LpVariable.dicts("L", range(qtd_setores), lowBound=0, upBound=H, cat="Continuous")

    # ==========
    # Variaveis binarias

    # bin de posicao entre maquinas
    esq_maq = LpVariable.dicts("esq", [(i, j) for i in range(qtd_maquinas) for j in range(qtd_maquinas)], cat="Binary")
    dir_maq = LpVariable.dicts("dir", [(i, j) for i in range(qtd_maquinas) for j in range(qtd_maquinas)], cat="Binary")
    cima_maq = LpVariable.dicts("cima", [(i, j) for i in range(qtd_maquinas) for j in range(qtd_maquinas)], cat="Binary")
    baixo_maq = LpVariable.dicts("baixo", [(i, j) for i in range(qtd_maquinas) for j in range(qtd_maquinas)], cat="Binary")

    # bin de posicao entre setores
    esq_set = LpVariable.dicts("esq_set", [(i, j) for i in range(qtd_setores) for j in range(qtd_setores)], cat="Binary")
    dir_set = LpVariable.dicts("dir_set", [(i, j) for i in range(qtd_setores) for j in range(qtd_setores)], cat="Binary")
    cima_set = LpVariable.dicts("cima_set", [(i, j) for i in range(qtd_setores) for j in range(qtd_setores)], cat="Binary")
    baixo_set = LpVariable.dicts("baixo_set", [(i, j) for i in range(qtd_setores) for j in range(qtd_setores)], cat="Binary")

    # ==========
    # Variavel de objetivo
    Largura_total = LpVariable("Largura_total", lowBound=0, upBound=W, cat="Continuous")
    # Funcao objetivo: minimizar a largura total ocupada pelas maquinas
    problema += Largura_total, "Minimizar a largura total ocupada pelas maquinas"

    # ============================================================
    # Restricoes

    # ==========
    # R1: Largura_total >= X_set + L_set para cada setor
    for i in range(qtd_setores):
        problema += (Largura_total >= X_set[i] + L_set[i]), f"Restricao_de_largura_total_{i}"

    # ==========
    # R2: Setor dentro da academia
    for i in range(qtd_setores):
        problema += (X_set[i] + L_set[i] <= W), f"Restricao_de_largura_setor_{i}"
        problema += (Y_set[i] + A_set[i] <= H), f"Restricao_de_altura_setor_{i}"

    # ==========
    # R3: Sobreposicao entre setores
    for i in range(qtd_setores):
        for j in range(i + 1, qtd_setores):
            # td setor tem q estar em pelo menos uma direcao do outro
            problema += (dir_set[(i, j)] + esq_set[(i, j)] + cima_set[(i, j)] + baixo_set[(i, j)] >= 1), f"Restricao_de_sobreposicao_{i}_{j}"

            # restricoes de sobreposicao entre setores
            problema += (X_set[i] + L_set[i] <= X_set[j] + W * (1 - dir_set[(i, j)])), f"Restricao_setor_{i}_esq_{j}"
            problema += (X_set[j] + L_set[j] <= X_set[i] + W * (1 - esq_set[(i, j)])), f"Restricao_setor_{j}_esq_{i}"
            problema += (Y_set[i] + A_set[i] <= Y_set[j] + H * (1 - cima_set[(i, j)])), f"Restricao_setor_{i}_cima_{j}"
            problema += (Y_set[j] + A_set[j] <= Y_set[i] + H * (1 - baixo_set[(i, j)])), f"Restricao_setor_{j}_cima_{i}"

    # ==========
    # R4: Maquinas dentro do setor
    for i in range(qtd_maquinas):
        # itens com posicao fixa sao tratados como obstaculos:
        # nao precisam ficar dentro de nenhum setor
        if maquinas_porQtd[i]["x_fixo"] is not None and maquinas_porQtd[i]["y_fixo"] is not None:
            continue

        # Pega o n do setor da maquina
        setor_index = setores.index(maquinas_porQtd[i]["setor"])

        # Confere se a maquina esta dentro do setor
        # tem q estar acima da parte de baixo(a direita da parte da esq)
        problema += (x_maq[i] >= X_set[setor_index]), f"Restricao_maquina_{i}_dentro_setor_x"
        problema += (y_maq[i] >= Y_set[setor_index]), f"Restricao_maquina_{i}_dentro_setor_y"
        # tem q estar abaixo da parte de cima(a esquerda da parte da dir)
        problema += (x_maq[i] + maquinas_porQtd[i]["w"] <= X_set[setor_index] + L_set[setor_index]), f"Restricao_maquina_{i}_dentro_setor_x2"
        problema += (y_maq[i] + maquinas_porQtd[i]["h"] <= Y_set[setor_index] + A_set[setor_index]), f"Restricao_maquina_{i}_dentro_setor_y2"

    # ==========
    # R5: Sobreposicao entre maquinas
    for i in range(qtd_maquinas):
        for j in range(i + 1, qtd_maquinas):
            # entre dois itens fixos nao adianta restringir aqui (posicoes sao
            # constantes); a nao-sobreposicao deles e' validada em Python (R6).
            if eh_fixa[i] and eh_fixa[j]:
                continue

            # td maquina tem q estar em pelo menos uma direcao do outro
            problema += (dir_maq[(i, j)] + esq_maq[(i, j)] + cima_maq[(i, j)] + baixo_maq[(i, j)] >= 1), f"Restricao_de_sobreposicao_maquina_{i}_{j}"

            # restricoes de sobreposicao entre maquinas
            problema += (x_maq[i] + maquinas_porQtd[i]["w"] <= x_maq[j] + W * (1 - dir_maq[(i, j)])), f"Restricao_maquina_{i}_esq_{j}"
            problema += (x_maq[j] + maquinas_porQtd[j]["w"] <= x_maq[i] + W * (1 - esq_maq[(i, j)])), f"Restricao_maquina_{j}_esq_{i}"
            problema += (y_maq[i] + maquinas_porQtd[i]["h"] <= y_maq[j] + H * (1 - cima_maq[(i, j)])), f"Restricao_maquina_{i}_cima_{j}"
            problema += (y_maq[j] + maquinas_porQtd[j]["h"] <= y_maq[i] + H * (1 - baixo_maq[(i, j)])), f"Restricao_maquina_{j}_cima_{i}"

    # ==========
    # R6: Itens com posicao fixa (pilares, recepcao, etc.)
    # trava x e y na coordenada informada (essas igualdades tem variavel do pulp).
    # a nao-sobreposicao (R5) ja impede que outras maquinas fiquem em cima.
    #
    # OBS: "caber dentro do galpao" e' so com numeros (x_fixo + w <= W), entao
    # nao pode virar restricao do pulp -> e' validado em Python abaixo.
    itens_fora = []  # itens fixos que nao cabem no galpao na posicao dada
    eps = 1e-6
    for i in range(qtd_maquinas):
        x_fixo = maquinas_porQtd[i]["x_fixo"]
        y_fixo = maquinas_porQtd[i]["y_fixo"]
        if x_fixo is None or y_fixo is None:
            continue

        problema += (x_maq[i] == x_fixo), f"Restricao_maquina_{i}_x_fixo"
        problema += (y_maq[i] == y_fixo), f"Restricao_maquina_{i}_y_fixo"

        # validacao: a posicao fixa precisa manter o item inteiro dentro do galpao
        w = maquinas_porQtd[i]["w_real"]
        h = maquinas_porQtd[i]["h_real"]
        if (x_fixo < -eps or y_fixo < -eps
                or x_fixo + w > W + eps or y_fixo + h > H + eps):
            itens_fora.append(
                f"'{maquinas_porQtd[i]['nome']}' em ({x_fixo}, {y_fixo}) "
                f"tam {w}x{h}"
            )

    # se algum item fixo nao cabe, nem adianta resolver: retorna erro claro
    if itens_fora:
        return {
            "status": "Invalido",
            "sol_status": "Infeasible",
            "tem_solucao": False,
            "mensagem": (
                "Itens com posição fixa fora do galpão "
                f"({W} x {H} m):\n- " + "\n- ".join(itens_fora) +
                "\n\nAjuste as coordenadas X/Y desses itens (canto inferior-esquerdo)."
            ),
        }

    # validacao: dois itens fixos nao podem ocupar o mesmo espaco (senao infactivel).
    # usa o tamanho real (folga nao se aplica entre obstaculos fixos).
    fixos = [i for i in range(qtd_maquinas) if eh_fixa[i]]
    pares_sobrepostos = []
    for a in range(len(fixos)):
        for b in range(a + 1, len(fixos)):
            i, j = fixos[a], fixos[b]
            xi, yi = maquinas_porQtd[i]["x_fixo"], maquinas_porQtd[i]["y_fixo"]
            xj, yj = maquinas_porQtd[j]["x_fixo"], maquinas_porQtd[j]["y_fixo"]
            wi, hi = maquinas_porQtd[i]["w_real"], maquinas_porQtd[i]["h_real"]
            wj, hj = maquinas_porQtd[j]["w_real"], maquinas_porQtd[j]["h_real"]
            # sobrepoe se ha intersecao em x E em y
            if (xi < xj + wj - eps and xj < xi + wi - eps
                    and yi < yj + hj - eps and yj < yi + hi - eps):
                pares_sobrepostos.append(
                    f"'{maquinas_porQtd[i]['nome']}' e '{maquinas_porQtd[j]['nome']}'"
                )

    if pares_sobrepostos:
        return {
            "status": "Invalido",
            "sol_status": "Infeasible",
            "tem_solucao": False,
            "mensagem": (
                "Itens com posição fixa sobrepostos (ocupam o mesmo espaço):\n- "
                + "\n- ".join(pares_sobrepostos) +
                "\n\nAjuste as coordenadas X/Y para que não fiquem um sobre o outro."
            ),
        }

    # ============================================================
    # Resolve o problema com CBC
    # timeLimit faz o CBC parar e devolver a melhor solucao viavel encontrada
    # msg=True mostra o progresso do solver no terminal
    problema.solve(pulp.PULP_CBC_CMD(timeLimit=tempo_limite, msg=True))

    # ====================
    # decide se a solucao e factivel (pode ser desenhada)

    # todas as maquinas precisam ter recebido uma posicao
    tem_valores = all(
        x_maq[i].varValue is not None and y_maq[i].varValue is not None
        for i in range(qtd_maquinas)
    )

    # sol_status distingue "otima/inteira factivel" de "inviavel/sem solucao"
    # (mais confiavel que o status geral, que pode vir de uma relaxacao)
    sol_status = getattr(problema, "sol_status", None)
    if sol_status is not None:
        factivel = sol_status in (LpSolutionOptimal, LpSolutionIntegerFeasible)
    else:
        # pulp antigo sem sol_status: cai no status geral
        factivel = LpStatus[problema.status] == "Optimal"

    # so e desenhavel se for factivel E tiver valores em todas as maquinas
    tem_solucao = factivel and tem_valores

    # Obter resultados com CBC
    resultado_cbc = {
        "status": LpStatus[problema.status],
        "sol_status": LpSolution[sol_status] if sol_status is not None else "?",
        "tem_solucao": tem_solucao,
        "Larga_usada": value(problema.objective),
        "x_maq": {i: x_maq[i].varValue for i in range(qtd_maquinas)},
        "y_maq": {i: y_maq[i].varValue for i in range(qtd_maquinas)},
        "X_set": {i: X_set[i].varValue for i in range(qtd_setores)},
        "Y_set": {i: Y_set[i].varValue for i in range(qtd_setores)},
        "A_set": {i: A_set[i].varValue for i in range(qtd_setores)},
        "L_set": {i: L_set[i].varValue for i in range(qtd_setores)},

        # dados extras pra desenhar o layout
        "W": W,
        "H": H,
        "folga": folga,
        "setores": setores,
        "maquinas": [
            {
                "nome": maquinas_porQtd[i]["nome"],
                "w": maquinas_porQtd[i]["w_real"],
                "h": maquinas_porQtd[i]["h_real"],
                "setor": maquinas_porQtd[i]["setor"],
                "fixa": maquinas_porQtd[i]["x_fixo"] is not None
                        and maquinas_porQtd[i]["y_fixo"] is not None,
            }
            for i in range(qtd_maquinas)
        ],
    }
    
    # ============================================================
    # mostra os resultados no terminal

    # printar os setores com suas posicoes e dimensoes


    # printar cada maquina e sua posicao


    return resultado_cbc
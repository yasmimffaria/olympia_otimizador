from pulp import *

def resolver(W, H, folga, maquinas):
    print("Rodando otimização...")
    print(f"Galpão: {W}x{H}, Folga: {folga}")
    print("Máquinas:", maquinas)
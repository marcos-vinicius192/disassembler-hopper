"""
Hopper.py
Contador: 0

Numero de registradores: 8 (R0..R7) de 16 bits cada
Tamanho da memória: 65536 bytes (Mais que a Memória RAM de um Commodore 64)
Opcodes (instruções):
- 0x01: MOV_REG_IMM (Move valor imediato para registrador)
- 0x02: MOV_REG_REG (Move valor de um registrador para outro)
- 0x03: ADD_REG_REG (Adiciona valor de um registrador a outro)
- 0x10: JMP (Pula para endereço)
- 0x11: JZ (Pula para endereço se o flag zero estiver setado)
- 0xFF: HLT (Halt - para a execução)

opções de menu:
1) Carregar arquivo binário
2) Desmontar arquivo carregado
3) Executar (interpretar)
4) Modo Passo-a-passo
5) Mostrar registradores
6) Salvar desmontagem para arquivo
7) Sair

Registradores:
- R0..R7: Registradores gerais de 16 bits



bandeira:
- Z: Zero flag (setado se o resultado da última operação foi zero)

"""

from typing import List, Tuple, Optional # Tipagem
import struct # structs dos operandos
import sys # Operações do sistema
import os # Para verificação de arquivo

TAMNH_MEMO = 0x10000  # 65536 bytes de memória (65.5 KiloBytes)
REGIS_NUM = 8        # Numero de registradores

# Opcodes
OP_MOV_REG_IMM = 0x01
OP_MOV_REG_REG = 0x02
OP_ADD_REG_REG = 0x03
OP_JMP         = 0x10
OP_JZ          = 0x11
OP_HLT         = 0xFF

NOMES_OP = {
    OP_MOV_REG_IMM: "MOV_REG_IMM",
    OP_MOV_REG_REG: "MOV_REG_REG",
    OP_ADD_REG_REG: "ADD_REG_REG",
    OP_JMP:         "JMP",
    OP_JZ:          "JZ",
    OP_HLT:         "HLT"
}

# pc - Registrador de Contador de programa
# bandeira - Registrador de Status da CPU

class CPU:
    def __init__(self):
        self.regs = [0] * REGIS_NUM 
        self.pc = 0                 
        self.bandeira = {"Z": False}   
        self.parou = False

    def resetar_Processador(self):
        self.regs = [0] * REGIS_NUM
        self.pc = 0
        self.bandeira = {"Z": False}
        self.parou = False

    def dump(self) -> str:
        regs_str = " ".join(f"R{i}={self.regs[i]:04X}" for i in range(REGIS_NUM))
        return f"PC={self.pc:04X} {regs_str} Z={int(self.bandeira['Z'])} HALT={self.parou}"

def carregar_arquivo(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def u8(data: bytes, idx: int) -> Tuple[int, int]:
    if idx >= len(data):
        return (0, idx + 1)
    return (data[idx], idx + 1)

def u16_le(data: bytes, idx: int) -> Tuple[int, int]:
    if idx + 1 >= len(data):
        lo = data[idx] if idx < len(data) else 0
        hi = data[idx + 1] if (idx + 1) < len(data) else 0
        return (lo | (hi << 8), idx + 2)
    lo = data[idx]
    hi = data[idx + 1]
    return (lo | (hi << 8), idx + 2)

def desmontar(raw: bytes) -> List[str]:
    out = []
    i = 0
    n = len(raw)
    while i < n:
        enderec = i
        opcode, i = u8(raw, i)
        if opcode == OP_MOV_REG_IMM:
            reg, i = u8(raw, i)
            imm, i = u16_le(raw, i)
            out.append(f"{enderec:04X}: MOV R{reg}, #{imm}    ; [{opcode:02X}]")
        elif opcode == OP_MOV_REG_REG:
            dst, i = u8(raw, i)
            src, i = u8(raw, i)
            out.append(f"{enderec:04X}: MOV R{dst}, R{src}    ; [{opcode:02X}]")
        elif opcode == OP_ADD_REG_REG:
            dst, i = u8(raw, i)
            src, i = u8(raw, i)
            out.append(f"{enderec:04X}: ADD R{dst}, R{src}    ; [{opcode:02X}]")
        elif opcode == OP_JMP:
            enderec16, i = u16_le(raw, i)
            out.append(f"{enderec:04X}: JMP {enderec16:04X}    ; [{opcode:02X}]")
        elif opcode == OP_JZ:
            enderec16, i = u16_le(raw, i)
            out.append(f"{enderec:04X}: JZ  {enderec16:04X}    ; [{opcode:02X}]")
        elif opcode == OP_HLT:
            out.append(f"{enderec:04X}: HLT    ; [{opcode:02X}]")
        else:
            out.append(f"{enderec:04X}: DB 0x{opcode:02X}")
    return out

def memoria_de_bytes_lidos(bytes_lidos: bytes) -> bytearray:
    mem = bytearray(TAMNH_MEMO)
    mem[:len(bytes_lidos)] = bytes_lidos
    return mem

def fetch_u8(mem: bytearray, enderec: int) -> int:
    if 0 <= enderec < len(mem):
        return mem[enderec]
    return 0

def fetch_u16_le(mem: bytearray, enderec: int) -> int:
    lo = fetch_u8(mem, enderec)
    hi = fetch_u8(mem, enderec + 1)
    return lo | (hi << 8)

def executar_todos_passos(mem: bytearray, cpu: CPU, tamnh_programa: Optional[int] = None, passos_maximos: Optional[int] = None) -> CPU:

    steps = 0
    limite = len(mem) if tamnh_programa is None else tamnh_programa
    if limite < 0:
        limite = 0
    if limite > len(mem):
        limite = len(mem)

    while not cpu.parou and 0 <= cpu.pc < limite:
        if passos_maximos is not None and steps >= passos_maximos:
            break
        steps += 1
        cada_passo(mem, cpu)
    return cpu

def cada_passo(mem: bytearray, cpu: CPU) -> None:
    if cpu.parou:
        return
    comeco_contagem = cpu.pc
    opcode = fetch_u8(mem, comeco_contagem)


    increm_contagem = comeco_contagem + 1

    if opcode == OP_MOV_REG_IMM:
        reg = fetch_u8(mem, comeco_contagem + 1)
        imm = fetch_u16_le(mem, comeco_contagem + 2)
        if 0 <= reg < REGIS_NUM:
            cpu.regs[reg] = imm & 0xFFFF
        increm_contagem = comeco_contagem + 4
    elif opcode == OP_MOV_REG_REG:
        dst = fetch_u8(mem, comeco_contagem + 1)
        src = fetch_u8(mem, comeco_contagem + 2)
        if 0 <= dst < REGIS_NUM and 0 <= src < REGIS_NUM:
            cpu.regs[dst] = cpu.regs[src]
        increm_contagem = comeco_contagem + 3
    elif opcode == OP_ADD_REG_REG:
        dst = fetch_u8(mem, comeco_contagem + 1)
        src = fetch_u8(mem, comeco_contagem + 2)
        if 0 <= dst < REGIS_NUM and 0 <= src < REGIS_NUM:
            result = (cpu.regs[dst] + cpu.regs[src]) & 0xFFFF
            cpu.regs[dst] = result
            cpu.bandeira["Z"] = (result == 0)
        increm_contagem = comeco_contagem + 3
    elif opcode == OP_JMP:
        enderec = fetch_u16_le(mem, comeco_contagem + 1)
        increm_contagem = enderec & 0xFFFF
    elif opcode == OP_JZ:
        enderec = fetch_u16_le(mem, comeco_contagem + 1)
        if cpu.bandeira.get("Z", False):
            increm_contagem = enderec & 0xFFFF
        else:
            increm_contagem = comeco_contagem + 3
    elif opcode == OP_HLT:
        cpu.parou = True
        increm_contagem = comeco_contagem + 1
    else:
        # Unknown: treat as data / NOP and just advance one byte
        increm_contagem = comeco_contagem + 1

    cpu.pc = increm_contagem

def imprimir_desmont(lines: List[str]) -> None:
    for ln in lines:
        print(ln)

def salvar_desmontagem(lines: List[str], caminho_saida: str) -> None:
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")

def caminho_prompt(prompt: str) -> str:
    return input(prompt).strip('"').strip()

def loop_menu():
    bytes_lidos = b"" 
    mem = memoria_de_bytes_lidos(bytes_lidos)
    cpu = CPU()
    cache_desmont: List[str] = []
    caminho_arq_saida = None

    while True:
        print("\n=== Disassembler Hopper ===")
        print("1) Carregar arquivo binário")
        print("2) Desmontar arquivo carregado")
        print("3) Executar (interpretar)")
        print("4) Modo Passo-a-passo")
        print("5) Mostrar registradores")
        print("6) Salvar desmontagem para arquivo")
        print("7) Sair")
        escolha_opc = input("Selecionar: ").strip()

        if escolha_opc == "1":
            path = caminho_prompt("Inserir caminho do arquivo binário: ")
            if not os.path.isfile(path):
                print("Arquivo não encontrado.")
                continue
            try:
                bytes_lidos = carregar_arquivo(path)
                mem = memoria_de_bytes_lidos(bytes_lidos)
                cpu.resetar_Processador()
                cache_desmont = []
                caminho_arq_saida = path
                print(f"Carregados {len(bytes_lidos)} bytes de {path}")
                print(f"Primeiros bytes carregados: {bytes_lidos[:16].hex()}")
            except Exception as e:
                print("Error loading file:", e)

        elif escolha_opc == "2":
            if not bytes_lidos:
                print("Nenhum binário carregado. Carregar arquivo primeiro (opção 1).")
                continue
            cache_desmont = desmontar(bytes_lidos)
            imprimir_desmont(cache_desmont[:10000])  # safe cap
            print(f"\n{len(cache_desmont)} linhas desmontadas.")

        elif escolha_opc == "3":
            if not bytes_lidos:
                print("Nenhum binário carregado.")
                continue
            cpu.resetar_Processador()
            mem = memoria_de_bytes_lidos(bytes_lidos)
            executar_todos_passos(mem, cpu, tamnh_programa=len(bytes_lidos))
            print("Execução completa.")
            print(cpu.dump())

        elif escolha_opc == "4":
            if not bytes_lidos:
                print("Nenhum binário carregado.")
                continue
            cpu.resetar_Processador()
            mem = memoria_de_bytes_lidos(bytes_lidos)
            print("Entrando em modo passo-a-passo. Comandos: 'p' passo, 'c' continue, 'r' registradores, 's' sair")
            while True:
                print(cpu.dump())
                cmd_passo = input("modo-passo> ").strip().lower()
                if cmd_passo in ("p", "passo"):
                    cada_passo(mem, cpu)
                elif cmd_passo in ("c", "cont", "continue"):
                    executar_todos_passos(mem, cpu, tamnh_programa=len(bytes_lidos))
                    print("Continuou para o fim ou saída.")
                    break
                elif cmd_passo in ("r", "regitradores"):
                    print(cpu.dump())
                elif cmd_passo in ("s", "quit", "sair"):
                    break
                else:
                    print("Comando de passo desconhecido.")
            print("Saindo do modo passo-a-passo.")

        elif escolha_opc == "5":
            print(cpu.dump())

        elif escolha_opc == "6":
            if not cache_desmont:
                if not bytes_lidos:
                    print("Nenhum binário carregado para Desmontar.")
                    continue
                cache_desmont = desmontar(bytes_lidos)
            caminho_saida = caminho_prompt("Caminho de saída para desmontagem: ")
            try:
                salvar_desmontagem(cache_desmont, caminho_saida)
                print(f"Desmontagem salvo para {caminho_saida}")
            except Exception as e:
                print("Falhou em Salvar", e)

        elif escolha_opc == "7":
            print("Saindo.")
            break

        else:
            print("Opção inválida.")

def main():
    try:
        loop_menu()
    except KeyboardInterrupt:
        print("\nProcesso Interronpido. Saindo.")
        sys.exit(0)

if __name__ == "__main__":
    main()

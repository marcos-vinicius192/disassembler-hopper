# <center> HOPPER </center>
###### <center> *28/10/2025* </center>
---

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://img.shields.io/badge/Python-3.13-blue)

O Disassembler *Hopper* é uma ferramenta de linha de comando que traduz arquivos binários de arquitetura própria em código assembly legível. Um desmontador (disassembler) é um programa de computador que converte linguagem de máquina em linguagem de montagem, realizando a operação inversa de um montador.

Hopper vem com um menu de input de arquivos binários e opções de operações com ele

Este projeto tem como objetivo simplificar a análise de pequenos programas binários, facilitando tarefas de engenharia reversa e entendimento do funcionamento interno do código.

O Hopper interpreta os bytes de entrada conforme o conjunto de instruções:
```
- 0x01: MOV_REG_IMM (Move valor imediato para registrador)
- 0x02: MOV_REG_REG (Move valor de um registrador para outro)
- 0x03: ADD_REG_REG (Adiciona valor de um registrador a outro)
- 0x10: JMP (Pula para endereço)
- 0x11: JZ (Pula para endereço se o flag zero estiver setado)
- 0xFF: HLT (Halt - para a execução)
```
 
 Exibindo no console as instruções correspondentes em assembly legível. Por ser multiplataforma, funciona tanto em Windows quanto em Linux sem modificações.

## Pré-Requisitos
* Python 3.13.3 
* Py-Installer

## Exemplos 

### Teste 1: Subtração
```
OPCODES:
  0x01 MOV_REG_IMM   
  0x02 MOV_REG_REG   
  0x03 ADD_REG_REG   
  0x10 JMP           
  0x11 JZ              
  0xFF HLT           
```
### Teste 2: Multiplicação
```
    MOV R0, #0        ; acumulador (resultado)
    MOV R1, #4        ; multiplicando
    MOV R2, #3        ; multiplicador
    MOV R3, R2        ; contador = R2
    MOV R7, #0xFFFF   ; -1 para decrementar
LOOP:
    ADD R0, R1        ; R0 += R1
    ADD R3, R7        ; R3 -= 1  (Z set se chegou a 0)
    JZ END
    JMP LOOP
END:
    HLT
```
### Teste 3: Fibonacci
```
    MOV R0, #0        ; F0
    MOV R1, #1        ; F1
    MOV R3, #5        ; número de iterações
    MOV R7, #0xFFFF   ; -1 para decrementar R3
LOOP:
    MOV R2, R0        ; R2 = R0
    ADD R2, R1        ; R2 = R0 + R1  (novo termo)
    MOV R0, R1        ; desloca: R0 <- antigo R1
    MOV R1, R2        ; desloca: R1 <- novo termo
    ADD R3, R7        ; R3 -= 1
    JZ END
    JMP LOOP
END:
    HLT

```
### Teste 4: Contagem
```
    MOV R0, #3          ; inicial contador
    MOV R7, #0xFFFF     ; constante -1
LOOP:
    ADD R0, R7          ; R0 = R0 - 1
    JZ END              ; se zero, sai
    JMP LOOP
END:
    HLT

```

#### <center> Diagrama (mermaid) de Sistema </center>
```mermaid
flowchart TB
  HOPPER["Hopper.py\nContador: 0"] --> MENU["Menu (loop_menu)\nOpções:\n1) Carregar arquivo binário (carregar_arquivo)\n2) Desmontar (desmontar)\n3) Executar (executar_todos_passos)\n4) Modo Passo-a-passo (cada_passo)\n5) Mostrar registradores (CPU.dump)\n6) Salvar desmontagem (salvar_desmontagem)\n7) Sair"]

  MENU --> CARREGAR["carregar_arquivo(path)"]
  CARREGAR --> BYTES["bytes_lidos (bytes) - conteúdo bruto lido"]

  BYTES --> DESM["desmontar(bytes_lidos)\n-> lista de linhas (cache_desmont)"]
  DESM --> IMPR["imprimir_desmont(lines)"]
  DESM --> SALVAR["salvar_desmontagem(lines, caminho_saida)"]

  BYTES --> MEMLOAD["memoria_de_bytes_lidos(bytes_lidos)\n-> bytearray(TAMNH_MEMO)"]
  MEMLOAD --> MEM["Memória (bytearray)\nTAMNH_MEMO = 0x10000 (65536 bytes)"]

  MEM --> EXEC["executar_todos_passos(mem, cpu, tamnh_programa=len(bytes_lidos))"]
  EXEC --> CPUOBJ["CPU (classe CPU)"]

  subgraph CPU["Estrutura da CPU (instância)"]
    REGS["regs: R0..R7 (8 registradores, 16-bit)"]
    PC["pc: Contador de Programa (inicio 0)"]
    FLAGS["bandeira: {'Z': bool} (Zero flag)"]
    HALT["parou: bool (HLT)"]
  end

  CPUOBJ --> REGS
  CPUOBJ --> PC
  CPUOBJ --> FLAGS
  CPUOBJ --> HALT

  %% Helpers
  subgraph HELPERS["Funções auxiliares / Fetch & Parsers"]
    U8["u8(data, idx)"]
    U16["u16_le(data, idx)"]
    FETCH8["fetch_u8(mem, addr)"]
    FETCH16["fetch_u16_le(mem, addr)"]
  end

  DESM --> U8
  DESM --> U16
  EXEC --> FETCH8
  EXEC --> FETCH16

  %% Opcodes (detalhados)
  subgraph OPCODES["Conjunto de Instruções / Opcodes (implementadas)"]
    O1["0x01 MOV_REG_IMM\nFormato: [01][reg][imm_lo][imm_hi]\nSemântica: R[reg] = imediato"]
    O2["0x02 MOV_REG_REG\nFormato: [02][dst][src]\nSemântica: R[dst] = R[src]"]
    O3["0x03 ADD_REG_REG\nFormato: [03][dst][src]\nSemântica: R[dst] = R[dst] + R[src]; Z set se zero"]
    O4["0x10 JMP\nFormato: [10][addr_lo][addr_hi]\nSemântica: pc = endereço"]
    O5["0x11 JZ\nFormato: [11][addr_lo][addr_hi]\nSemântica: if Z then pc = endereço"]
    O6["0xFF HLT\nFormato: [FF]\nSemântica: parou = True"]
  end

  EXEC --> OPCODES
  OPCODES --> CPUOBJ

  %% Saída / Interação
  EXEC --> OUTPUT["Console / Saídas (print)\nModo passo-a-passo -> prompt 'modo-passo>'"]
  CPUOBJ --> OUTPUT

  %% Salvamento / FS
  SALVAR --> FS[(Sistema de Arquivos)]

````

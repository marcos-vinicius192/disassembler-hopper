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
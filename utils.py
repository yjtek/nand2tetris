from typing import Callable, Any
import random
import re
import itertools
import copy
from dataclasses import dataclass

# Copies of the implementations in notebooks 2-9. A change in a notebook must be copied here too.

POWER = True
GROUND = None
type TRANSISTOR_OUTPUT = bool | None


# ------------------------------ 2_transistors_to_logic.ipynb

def pmos(gate_signal: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    """
    Pass through source signal when gate_signal is False (i.e. low power)
    None when gate_signal is True (i.e. high power)
    """
    return source if not gate_signal else None


def nmos(gate_signal: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    """
    Pass through source signal when gate_signal is True (i.e. high power)
    None when gate_signal is False (i.e low power)
    """
    return source if gate_signal else None


def pmos_NAND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                     POWER (1)
                  ┌─────┴─────┐
                  │           │
     Input1 --> [PMOS A]    [PMOS B] <-- Input2
                  │           │
                  └─────┬─────┘
                        ├─── OUTPUT (Out)
                        │
                    [Resistor]
                        │
                    GROUND (0)
    '''
    # If input1 and input2 are both True, both PMOS return None, and so no output is returned
    # Otherwise, so long as one of input1/input2 are False, the power flows through one of the PMOS paths and 
    # output returns True
    pmos_A = pmos(input1, source)
    pmos_B = pmos(input2, source)
    
    return POWER if pmos_A or pmos_B else GROUND


def pmos_NOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
        [PMOS A] <-- Input1
            │             
        [PMOS B] <-- Input2
            │
            ├─── OUTPUT (Out)
            │
        [Resistor]
            │
        GROUND (0)
    '''
    # If both input1 and input2 are None, both PMOS transistors let power through, and Output is POWER
    # Else if either input1 or input2 are True, the circuit breaks, and ground is returned
    pmos_A = pmos(input1, source)
    pmos_B = pmos(input2, pmos_A)

    return POWER if pmos_B else GROUND


def pmos_NOT(input1: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
         [PMOS] <-- Input1
            │
            ├─── OUTPUT (Out)
            │
        [Resistor]
            │
        GROUND (0)
    '''
    ## PMOS negates the input by construction, because it outputs 0 if input is 1
    out1 = pmos(input1, source)
    return POWER if out1 else GROUND


def pmos_AND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                     POWER (1)
                  ┌─────┴─────┐
                  │           │
     Input1 --> [PMOS A]    [PMOS B] <-- Input2
                  │           │
                  └─────┬─────┘
                        ├─── NAND Output
                        │
                    [Resistor]
                        │
                    GROUND (0)
                        │
                     POWER (1)
                        │
                    [PMOS NOT] <-- NAND Output
                        │
                        ├─── OUTPUT (AND Out)
                        │
                    [Resistor]
                        │
                    GROUND (0)
    '''

    ## - If both input1 and input2 are 1, then the NAND Output is 0
    ##    - If the NAND output is 0, the NOT output is 1
    ## - Else the NAND output is 1
    ##    - If the NAND output is 1, the NOT output is 0
    ## - Therefore, the truth table becomes equivalent to AND
    ##    - (1,1) -> 1
    ##    - (0,1) -> 0
    ##    - (1,0) -> 0
    ##    - (0,0) -> 0

    nand_out = pmos_NAND(input1, input2, source=source)
    return pmos_NOT(nand_out, source=source)


def pmos_OR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                    POWER (1)
                        │
     Input1 -------> [PMOS A]
                        │             
     Input2 -------> [PMOS B]
                        │
                        ├─── Intermediate (NOR)
                        │
                    [Resistor]
                        │
                    GROUND (0)
                        │
                     POWER (1)
                        │
                    [PMOS NOT] <-- Intermediate (NOR)
                        │
                        ├─── OUTPUT (OR Out)
                        │
                    [Resistor]
                        │
                    GROUND (0)
    '''
    ## - If both input1 and input2 are 0, then the NOR Output is 1
    ##    - If the NOR output is 1, the NOT output is 0
    ## - Else the NOR output is 0
    ##    - If the NOR output is 0, the NOT output is 1
    ## - Therefore, the truth table becomes equivalent to OR
    ##    - (1,1) -> 1
    ##    - (0,1) -> 1
    ##    - (1,0) -> 1
    ##    - (0,0) -> 0
    nor_out = pmos_NOR(input1, input2, source=source)
    return pmos_NOT(nor_out, source=source)


def pmos_XNOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
      ┌─────┴─────────────────────┐
      │ Branch 1 (0, 0)           │ Branch 2 (1, 1)
  [PMOS A]  <-- Input1        [PMOS A'] <-- NOT(Input1)
      │                           │
  [PMOS B]  <-- Input2        [PMOS B'] <-- NOT(Input2)
      └─────┬─────────────────────┘
            ├─── OUTPUT (Out)
            │
        [Resistor]
            │
        GROUND (0)
    '''
    ## - If (0, 0) --> 1
    ##    - PMOS A and B both return 1, PMOS A' and B' both return 0
    ##    - POWER hits output, returns 1
    ## - If (0, 1) --> 0
    ##    - A returns 1 and B returns 0, A' returns 0 and B' returns 1
    ##    - Both circuts break, returns 0
    ## - If (1, 0) --> 0
    ##    - Same as (0, 1) case
    ## - If (1, 1)
    ##    - A and B both return 0, A' and B' both return 1
    ##    - POWER hits output, returns 1

    input1_inv = pmos_NOT(input1, source)
    input2_inv = pmos_NOT(input2, source)

    pmos_A = pmos(input1, source)
    pmos_B = pmos(input2, pmos_A)

    pmos_A2 = pmos(input1_inv, source)
    pmos_B2 = pmos(input2_inv, pmos_A2)

    return POWER if pmos_B or pmos_B2 else GROUND


def pmos_XOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
              Input1    Input2
                 │         │
        ┌────────┼─────────┼────────┐
        │        │         │        │
        ▼        ▼         ▼        ▼
     ┌──────────────┐   ┌──────────────┐
     │   pmos_OR    │   │  pmos_NAND   │
     └──────┬───────┘   └──────┬───────┘
            │                  │
         OR Out             NAND Out
            │                  │
            └────────┬─────────┘
                     │
                     ▼
             ┌──────────────┐
             │   pmos_AND   │
             └──────┬───────┘
                    │
                    ▼
                 OUTPUT
    '''
    ## - If (0, 0) --> 0
    ##    - PMOS OR returns 0, PMOS NAND returns 1
    ##    - PMOS AND returns 0
    ## - If (0, 1) --> 1
    ##    - PMOS OR returns 1, PMOS NAND returns 1
    ##    - PMOS AND returns 1    
    ## - If (1, 0) --> 1
    ##    - PMOS OR returns 1, PMOS NAND returns 1
    ##    - PMOS AND returns 1
    ## - If (1, 1) --> 0
    ##    - PMOS OR returns 1, PMOS NAND returns 0
    ##    - PMOS AND returns 0
    or_out = pmos_OR(input1, input2, source=source)
    nand_out = pmos_NAND(input1, input2, source=source)
    return pmos_AND(or_out, nand_out, source=source)


def nmos_NAND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
        [Resistor]
            │
            ├─── OUTPUT (Out)
            │
        [NMOS A] <-- Input1
            │
        [NMOS B] <-- Input2
            │
        GROUND (0)
    '''
    ## If both input1 and input2 are 1, NMOS outputs 1. 
    ## Therefore, series goes to ground. Else output 1
    nmos_A = nmos(input1, power)
    nmos_B = nmos(input2, nmos_A)
    return GROUND if nmos_B else power


def nmos_NOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                    POWER (1)
                        │
                    [Resistor]
                        │
                        ├─── OUTPUT (Out)
                  ┌─────┴─────┐
                  │           │
     Input1 --> [NMOS A]    [NMOS B] <-- Input2
                  │           │
                  └─────┬─────┘
                        │
                    GROUND (0)
    '''
    ## If both input1 and input2 are 0, NMOS outputs 0. 
    ## Therefore, outputs 1. Else output GROUND
    nmos_A = nmos(input1, power)
    nmos_B = nmos(input2, power)
    return GROUND if (nmos_A or nmos_B) else power


def nmos_NOT(input1: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
        [Resistor]
            │
            ├─── OUTPUT (Out)
            │
        [NMOS] <-- Input
            │
        GROUND (0)
    '''
    # When input1 is 0, NMOS outputs 0, which breaks the circuit to ground. Therefore, output is 1
    nmos_out = nmos(input1, power)
    return GROUND if nmos_out else power


def nmos_AND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
        [Resistor]
            │
            ├─── Intermediate (NAND)
            │
        [NMOS A] <-- Input1
            │
        [NMOS B] <-- Input2
            │
        GROUND (0)
            
         POWER (1)
            │
        [Resistor]
            │
            ├─── OUTPUT (AND Out)
            │
        [NMOS C] <-- Intermediate (NAND)
            │
        GROUND (0)
    '''
    ## - If both input1 and input2 are 1, then the NAND Output is 0
    ##    - If the NAND output is 0, NMOS C output is 0, which lets the circuit output POWER
    ## - Else the NAND output is 1
    ##    - If the NAND output is 1, NMOC C output is 1, and the output goes to GROUND
    ## - Therefore, the truth table becomes equivalent to AND
    ##    - (1,1) -> 1
    ##    - (0,1) -> 0
    ##    - (1,0) -> 0
    ##    - (0,0) -> 0
    
    nand_out = nmos_NAND(input1, input2, power=power)
    return nmos_NOT(nand_out, power=power)
    return GROUND if not_out else POWER


def nmos_OR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                    POWER (1)
                        │
                    [Resistor]
                        │
                        ├─── Intermediate (NOR)
                  ┌─────┴─────┐
                  │           │
     Input1 --> [NMOS A]    [NMOS B] <-- Input2
                  │           │
                  └─────┬─────┘
                        │
                    GROUND (0)
                        
                     POWER (1)
                        │
                    [Resistor]
                        │
                        ├─── OUTPUT (OR Out)
                        │
                    [NMOS C] <-- Intermediate
                        │
                    GROUND (0)
    '''
    ## - If both input1 and input2 are 0, then the NOR Output is 1
    ##    - If the NOR output is 1, NMOS C output is 1, which pull circuit to GROUND
    ## - Else the NOR output is 0
    ##    - If the NOR output is 0, NMOS C output is 0, and circuit outputs POWER
    ## - Therefore, the truth table becomes equivalent to OR
    ##    - (1,1) -> 1
    ##    - (0,1) -> 1
    ##    - (1,0) -> 1
    ##    - (0,0) -> 0
    
    nor_out = nmos_NOR(input1, input2, power=power)
    return nmos_NOT(nor_out, power=power)


def nmos_XNOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
        POWER (1)
            │
        [Resistor]
            │
            ├─── OUTPUT (Out)
            │
      ┌─────┴─────────────────────┐
      │ Branch 1                  │ Branch 2 
  [NMOS A'] <-- NOT(Input1)   [NMOS A]  <-- Input1
      │                           │
  [NMOS B]  <-- Input2        [NMOS B'] <-- NOT(Input2)
      └─────┬─────────────────────┘
            │
        GROUND (0)
    '''
    ## - If (0, 0) --> 1
    ##    - A returns 0, B' returns 1
    ##    - A' returns 1, B returns 0
    ##    - Both drain paths blocked, so output is 1
    ## - If (0, 1) --> 0
    ##    - A returns 0, B' returns 0
    ##    - A' returns 1, B returns 1
    ##    - Left drain path connected, so output is 0
    ## - If (1, 0) --> 0
    ##    - A returns 1, B' returns 1
    ##    - A' returns 0, B returns 0
    ##    - Right drain path connected, so output is 0
    ## - If (1, 1)
    ##    - A returns 1, B' returns 0 
    ##    - A' returns 0, B returns 1
    ##    - Both drain paths blocked, so output is 1
    
    input1_inv = nmos_NOT(input1)
    input2_inv = nmos_NOT(input2)

    nmos_A = nmos(input1, power)
    nmos_B2 = nmos(input2_inv, nmos_A)

    nmos_A2 = nmos(input1_inv, power)
    nmos_B = nmos(input2, nmos_A2)
    
    if nmos_B is not None or nmos_B2 is not None:
        return GROUND
    else:
        return POWER


def nmos_XOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
    NMOS XOR constructed from fundamental NMOS building blocks:
    XOR = (A OR B) AND (A NAND B)
    
               Input1    Input2
                 │         │
        ┌────────┼─────────┼────────┐
        │        │         │        │
        ▼        ▼         ▼        ▼
     ┌──────────────┐   ┌──────────────┐
     │   nmos_OR    │   │  nmos_NAND   │
     └──────┬───────┘   └──────┬───────┘
            │                  │
         OR Out             NAND Out
            │                  │
            └────────┬─────────┘
                     │
                     ▼
             ┌──────────────┐
             │   nmos_AND   │
             └──────┬───────┘
                    │
                    ▼
                 OUTPUT
    '''
    ## - If (0, 0) --> 0
    ##    - NMOS OR returns 0, NMOS NAND returns 1
    ##    - NMOS AND returns 0
    ## - If (0, 1) --> 1
    ##    - NMOS OR returns 1, NMOS NAND returns 1
    ##    - NMOS AND returns 1    
    ## - If (1, 0) --> 1
    ##    - NMOS OR returns 1, NMOS NAND returns 1
    ##    - NMOS AND returns 1
    ## - If (1, 1) --> 0
    ##    - NMOS OR returns 1, NMOS NAND returns 0
    ##    - NMOS AND returns 0
    or_out = nmos_OR(input1, input2, power=power)
    nand_out = nmos_NAND(input1, input2, power=power)
    return nmos_AND(or_out, nand_out, power=power)


def cmos_NOT(input1: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                        POWER (1)
                            │
        Input1 ───────── [PMOS] (Pull-Up)
                            │
                            ├─── OUTPUT (Out)
                            │
        Input1 ───────── [NMOS] (Pull-Down)
                            │
                        GROUND (0)
    '''
    ## - If input1 is 0 (GROUND):
    ##    - PMOS turns ON, connecting OUTPUT directly to POWER
    ##    - NMOS turns OFF, blocking path to GROUND
    ##    - OUTPUT = POWER (1)
    ## - If input1 is 1 (POWER):
    ##    - PMOS turns OFF, blocking path to POWER
    ##    - NMOS turns ON, connecting OUTPUT directly to GROUND
    ##    - OUTPUT = GROUND (0)
    pmos_out = pmos(input1, power)
    nmos_out = nmos(input1, GROUND)

    if pmos_out is not None:
        return power
    if nmos_out is not None:
        return GROUND
    return None


def cmos_NAND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                        POWER (1)
                     ┌──────┴──────┐
                     │             │
        Input1 ─── [PMOS A]     [PMOS B] ─── Input2
                     │             │
                     └──────┬──────┘
                            ├─── OUTPUT (Out)
                            │
        Input1 ───────── [NMOS A]
                            │
        Input2 ───────── [NMOS B]
                            │
                        GROUND (0)
    '''
    ## - PMOS transistors in parallel (Pull-Up Network)
    ## - NMOS transistors in series (Pull-Down Network)
    ## - If BOTH inputs are 1:
    ##    - Both PMOS turn OFF, both NMOS turn ON
    ##    - Path to POWER blocked; path to GROUND connected
    ##    - OUTPUT = GROUND (0)
    ## - Else with at least one 0:
    ##    - At least one PMOS turns ON, NMOS series path broken
    ##    - OUTPUT = POWER (1)
    pmos_A = pmos(input1, power)
    pmos_B = pmos(input2, power)

    nmos_A = nmos(input1, GROUND)
    nmos_B = nmos(input2, nmos_A)

    if pmos_A or pmos_B:
        return power
    if nmos_B is not None:
        return GROUND
    return None


def cmos_NOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                        POWER (1)
                            │
        Input1 ───────── [PMOS A]
                            │
        Input2 ───────── [PMOS B]
                            │
                            ├─── OUTPUT (Out)
                     ┌──────┴──────┐
                     │             │
        Input1 ─── [NMOS A]     [NMOS B] ─── Input2
                     │             │
                     └──────┬──────┘
                            │
                        GROUND (0)
    '''
    ## - PMOS transistors in series (Pull-Up Network)
    ## - NMOS transistors in parallel (Pull-Down Network)
    ## - If BOTH inputs are 0:
    ##    - Both PMOS turn ON, both NMOS turn OFF
    ##    - Path to POWER connected; path to GROUND blocked
    ##    - OUTPUT = POWER (1)
    ## - Otherwise (at least one input is 1):
    ##    - At least one NMOS turns ON, PMOS series path broken
    ##    - OUTPUT = GROUND (0)
    pmos_A = pmos(input1, power)
    pmos_B = pmos(input2, pmos_A)

    nmos_A = nmos(input1, GROUND)
    nmos_B = nmos(input2, GROUND)

    if pmos_B is not None:
        return power
    if nmos_A or nmos_B:
        return GROUND
    return None


def cmos_AND(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                        POWER (1)
                     ┌──────┴──────┐
                     │             │
        Input1 ─── [PMOS A]     [PMOS B] ─── Input2
                     │             │
                     └──────┬──────┘
                            ├─── NAND Output
                            │
        Input1 ───────── [NMOS A]
                            │
        Input2 ───────── [NMOS B]
                            │
                        GROUND (0)
                            
                        POWER (1)
                            │
        NAND Out ─────── [PMOS C]
                            │
                            ├─── OUTPUT (AND Out)
                            │
        NAND Out ─────── [NMOS C]
                            │
                        GROUND (0)
    '''
    ## - If both inputs are 1:
    ##    -  NAND output is 0
    ##       - Then PMOS C is 1 and NMOS C is 0
    ##          - So OUTPUT (1)
    ## - Else:
    ##    -  NAND output is 1
    ##       - Then PMOS C is 0 and NMOS C is 1
    ##          - So GROUND (0)
    ## - Overall
    ##    - (1, 1) -> 1
    ##    - (1, 0) -> 0
    ##    - (0, 1) -> 0
    ##    - (0, 0) -> 0
    nand_out = cmos_NAND(input1, input2, power=power)
    return cmos_NOT(nand_out, power=power)


def cmos_OR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                        POWER (1)
                            │
        Input1 ───────── [PMOS A]
                            │
        Input2 ───────── [PMOS B]
                            │
                            ├─── NOR Output
                     ┌──────┴──────┐
                     │             │
        Input1 ─── [NMOS A]     [NMOS B] ─── Input2
                     │             │
                     └──────┬──────┘
                            │
                        GROUND (0)
                            
                        POWER (1)
                            │
        NOR Out ──────── [PMOS C]
                            │
                            ├─── OUTPUT (OR Out)
                            │
        NOR Out ──────── [NMOS C]
                            │
                        GROUND (0)
    '''
    ## - If both inputs are 0:
    ##    -  NOR output is 1
    ##       - Then PMOS C is 0 and NMOS C is 1
    ##          - So GROUND (0)
    ## - Else:
    ##    -  NOR output is 0
    ##       - Then PMOS C is 1 and NMOS C is 0
    ##          - So POWER (1)
    ## - Overall
    ##    - (1, 1) -> 1
    ##    - (1, 0) -> 1
    ##    - (0, 1) -> 1
    ##    - (0, 0) -> 0
    nor_out = cmos_NOR(input1, input2, power=power)
    return cmos_NOT(nor_out, power=power)


def cmos_XNOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
                POWER (1)
                    │
          ┌─────────┴─────────┐
          │ PMOS              │ PMOS 
      [PMOS A] Input1     [PMOS A'] <-- NOT(Input1)
          │                   │
      [PMOS B] Input2     [PMOS B'] <-- NOT(Input2)
          └─────────┬─────────┘
                    ├─── OUTPUT (Out)
          ┌─────────┴─────────┐
          │ NMOS              │ NMOS 
      [NMOS A'] NOT(Input1) [NMOS A]  <-- Input1
          │                   │
      [NMOS B] Input2       [NMOS B'] <-- NOT(Input2)
          └─────────┬─────────┘
                    │
                GROUND (0)
    '''
    # Inverted inputs
    input1_inv = cmos_NOT(input1)
    input2_inv = cmos_NOT(input2)

    # PMOS Pull-Up Network (connected to POWER)
    pmos_A = pmos(input1, power)
    pmos_B = pmos(input2, pmos_A)

    pmos_A2 = pmos(input1_inv, power)
    pmos_B2 = pmos(input2_inv, pmos_A2)

    # NMOS Pull-Down Network (connected to GROUND)
    nmos_A2 = nmos(input1_inv, GROUND)
    nmos_B = nmos(input2, nmos_A2)

    nmos_A = nmos(input1, GROUND)
    nmos_B2 = nmos(input2_inv, nmos_A)

    # Output evaluation
    if pmos_B == POWER or pmos_B2 == POWER:
        return POWER
    elif nmos_B == GROUND or nmos_B2 == GROUND:
        return GROUND
    else:
        return None  # Floating state


def cmos_XOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, power: bool = POWER) -> TRANSISTOR_OUTPUT:
    '''
    CMOS XOR constructed from fundamental CMOS building blocks:
    XOR = (A OR B) AND (A NAND B)
    
               Input1    Input2
                 │         │
        ┌────────┼─────────┼────────┐
        │        │         │        │
        ▼        ▼         ▼        ▼
     ┌──────────────┐   ┌──────────────┐
     │   cmos_OR    │   │  cmos_NAND   │
     └──────┬───────┘   └──────┬───────┘
            │                  │
         OR Out             NAND Out
            │                  │
            └────────┬─────────┘
                     │
                     ▼
             ┌──────────────┐
             │   cmos_AND   │
             └──────┬───────┘
                    │
                    ▼
                 OUTPUT
    '''
    ## - If (0, 0) --> 0
    ##    - CMOS OR returns 0, CMOS NAND returns 1
    ##    - CMOS AND returns 0
    ## - If (0, 1) --> 1
    ##    - CMOS OR returns 1, CMOS NAND returns 1
    ##    - CMOS AND returns 1    
    ## - If (1, 0) --> 1
    ##    - CMOS OR returns 1, CMOS NAND returns 1
    ##    - CMOS AND returns 1
    ## - If (1, 1) --> 0
    ##    - CMOS OR returns 1, CMOS NAND returns 0
    ##    - CMOS AND returns 0
    or_out = cmos_OR(input1, input2, power=power)
    nand_out = cmos_NAND(input1, input2, power=power)
    return cmos_AND(or_out, nand_out, power=power)


# ------------------------------ 3_logic_to_stateless_ops.ipynb

def half_adder(a: TRANSISTOR_OUTPUT, b: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
            A ───┬─────────┐
                 │  ┌───┐  ├─── [cmos_XOR] ─── Sum
            B ───┼──┤XOR│──┘
                 │  └───┘
                 │  ┌───┐
                 └──┤AND│────── [cmos_AND] ─── Carry
                    └───┘
    '''
    ## - If (0, 0) --> (sum: 0, carry: 0)
    ##    - XOR(0,0) = 0, AND(0,0) = 0
    ## - If (0, 1) --> (sum: 1, carry: 0)
    ##    - XOR(0,1) = 1, AND(0,1) = 0
    ## - If (1, 0) --> (sum: 1, carry: 0)
    ##    - XOR(1,0) = 1, AND(0,1) = 0
    ## - If (1, 1) --> (sum: 0, carry: 1)
    ##    - XOR(1,1) = 0, AND(0,1) = 1

    # Returns 1 if a != b, else 0
    sum_out = cmos_XOR(a, b)

    # Returns 1 if a == b == 1, else 0
    carry_out = cmos_AND(a, b)

    return sum_out, carry_out


def full_adder(a: TRANSISTOR_OUTPUT, b: TRANSISTOR_OUTPUT, c_in: TRANSISTOR_OUTPUT = GROUND) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
        A, B ──────> [Half Adder 1] ─── (Sum1, Carry1)
                           │
        Sum1, C_in ─> [Half Adder 2] ─── (Final Sum, Carry2)
                           │
        Carry1, Carry2 ─> [cmos_OR] ─── Final Carry Out

    Note that the maximum a full adder will be asked to add is 1+1+1, which means it will never exceed 3.
    This is why the output of a full adder can simply be a sum, carry
    The sum can only be 0 or 1, since it is the sum of 2 binary values
    The carry can represent a maximum of the 2^1 (since it is a carry, it represents the binary value for the 
    next significant position)

    - (0, 0, 0) -> (0, 0)
        - HA(a=0, b=0) = s1=0, c1=0
        - HA(s1=0, c=0) = s2=0, c2=0
        - OR(c1=0, c=0) = c3=0
        - Output(s2=0, c3=0)
    - (0, 0, 1) | (0, 1, 0) | (1, 0, 0) -> (1, 0)
        - HA(a=1, b=0) = s1=1, c1=0
        - HA(s1=1, c=0) = s2=1, c2=0
        - OR(c1=0, c2=0) = c3=0
        - Output(s2=1, c3=0)
    - (0, 1, 1) | (1, 1, 0) | (1, 0, 1) -> (0, 1)
        - HA(a=1, b=1) = s1=0, c1=1
        - HA(s1=0, c=0) = s2=0, c2=0
        - OR(c1=1, c2=0) = c3=1
        - Output(s2=0, c3=1)
    - (1, 1, 1) -> (1, 1)
        - HA(a=1, b=1) = s1=0, c1=1
        - HA(s1=0, c=1) = s2=1, c2=0
        - OR(c1=1, c2=0) = c3=1
        - Output(s2=1, c3=1)
    '''
    
    
    sum1, carry1 = half_adder(a, b)

    final_sum, carry2 = half_adder(sum1, c_in)
    
    final_carry = cmos_OR(carry1, carry2)
    return final_sum, final_carry


def ripple_carry_adder(a_bits: list[TRANSISTOR_OUTPUT], b_bits: list[TRANSISTOR_OUTPUT]) -> tuple[list[TRANSISTOR_OUTPUT], TRANSISTOR_OUTPUT]:
    '''
    Ripple-Carry Adder processing LSB to MSB.
    Takes two equal-length lists of bit signals (ordered LSB -> MSB).
    Returns (sum_bits, final_carry_out)

        LSB (Bit 0)                 Bit 1                    MSB (Bit 2)
        a_bits[0] = 1            a_bits[1] = 1              a_bits[2] = 1
        b_bits[0] = 1            b_bits[1] = 1              b_bits[2] = 1
                │                        │                          │
                │   ┌─────────┐          │   ┌─────────┐            │   ┌─────────┐
                ├───┤         │          ├───┤         │            ├───┤         │
                │   │ Full    │          │   │ Full    │            │   │ Full    │
                └───┤ Adder 0 │          └───┤ Adder 1 │            └───┤ Adder 2 │
                    │         │              │         │                │         │
    GROUND ─────────┤ c_in    │  ┌───────────┤ c_in    │    ┌───────────┤ c_in    │
    (c_in = 0)      │         │  │ (c_out=1) │         │    │ (c_out=1) │         │
                    │   c_out ├──┘           │   c_out ├────┘           │   c_out ├─── Final Carry
                    │   sum   ├──┐           │   sum   ├──┐             │   sum   ├──┐ (carry = 1)
                    └─────────┘  │           └─────────┘  │             └─────────┘  │
                                ▼                        ▼                          ▼
                            sum_bits[0]              sum_bits[1]                sum_bits[2]
                            (Sum = 0)                (Sum = 1)                  (Sum = 1)

    
    ============
       EXAMPLE
    ============
    - a_bits = 5 = [1,0,1]
    - b_bits = 3 = [0,1,1]
    - carry = 0
    - sum_bits = []
    
    - Going from LSB to MSB:
        - full_adder(a=1, b=1, c=0) 
            - s1=0, c1=1
            - sum_bits = [,0]
        - full_adder(a=0, b=1, c=c1=1)
            - s2=0, c2=1
            - sum_bits = [,0,0]
        - full_adder(a=1, b=0, c=c2=1)
            - s3=0, c3=1
            - sum_bits = [0,0,0]
    
    - Final value:
        - Concatenate sum_bits and prepend the final carry
        - output = 1000 = 8 = 5 + 3

    '''
    carry: TRANSISTOR_OUTPUT = GROUND
    sum_bits: list[TRANSISTOR_OUTPUT] = []
    
    for bit_a, bit_b in zip(a_bits, b_bits):
        s, carry = full_adder(bit_a, bit_b, carry)
        sum_bits.append(s)
        
    return sum_bits, carry


def mux_2to1(d0: TRANSISTOR_OUTPUT, d1: TRANSISTOR_OUTPUT, sel: TRANSISTOR_OUTPUT) -> TRANSISTOR_OUTPUT:
    '''
    2-to-1 MUX.
    Selects d0 when sel is GROUND (0), and d1 when sel is POWER (1).

            D0 ───┬─────────┐
                  │  ┌───┐  ├─── [cmos_AND] ─── Path0 ──┐
        ~Sel ─────┼──┤AND│──┘                           │
                  │  └───┘                              ├─── [cmos_OR] ─── Output
            D1 ───┼─────────┐                           │
                  │  ┌───┐  ├─── [cmos_AND] ─── Path1 ──┘
         Sel ─────┼──┤AND│──┘
                     └───┘
    
    Logic Truth Table:
    - If sel == 0:
        - ~sel = 1
        - path0 = AND(d0, ~sel)
            - If D0 = 0 => Output = 0
            - If D0 = 1 => Output = 1
        - path1 = AND(d1, sel)
            - If D1 = 0 => Output = 0
            - If D1 = 1 => Output = 0
        - Output = OR(path0, path1) = 1
    '''
    # Invert the selector bit to enable the d0 branch
    not_sel = cmos_NOT(sel)

    # Route d0 if sel is 0, route d1 if sel is 1
    path0 = cmos_AND(d0, not_sel)
    path1 = cmos_AND(d1, sel)

    # Combine the active path (only one path can be active at a time)
    return cmos_OR(path0, path1)


def mux_4to1(
    d0: TRANSISTOR_OUTPUT, 
    d1: TRANSISTOR_OUTPUT, 
    d2: TRANSISTOR_OUTPUT, 
    d3: TRANSISTOR_OUTPUT, 
    sel: tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]
) -> TRANSISTOR_OUTPUT:
    '''
    4-to-1 Multiplexer constructed hierarchically using 2-to-1 MUXes.
    
    Inputs:
    - d0, d1, d2, d3: Data lines
    - sel: (sel1, sel0) 
    
    Hierarchy Diagram:
        D0 ────┐
               ├─── [ MUX Stage 1: Level 0 ] ─── Out0 ──┐
        D1 ────┘                 │                      │
                             sel[0] (LSB)               ├─── [ MUX Stage 2 ] ─── Output
        D2 ────┐                                        │             │
               ├─── [ MUX Stage 1: Level 1 ] ─── Out1 ──┘         sel[1] (MSB)
        D3 ────┘                 │
                             sel[0] (LSB)

    - sel = (0, 0) -> Out0 = d0, Out1 = d2 -> Output = d0
    - sel = (0, 1) -> Out0 = d1, Out1 = d3 -> Output = d1
    - sel = (1, 0) -> Out0 = d0, Out1 = d2 -> Output = d2
    - sel = (1, 1) -> Out0 = d1, Out1 = d3 -> Output = d3
    '''
    sel1, sel0 = sel

    # Stage 1: Use sel0 (LSB) to select between pairs (d0 vs d1) and (d2 vs d3)
    level0_out = mux_2to1(d0, d1, sel0)
    level1_out = mux_2to1(d2, d3, sel0)

    # Stage 2: Use sel1 (MSB) to select between the winning pair from Stage 1
    return mux_2to1(level0_out, level1_out, sel1)


def n_bit_mux_2to1(
    a_word: list[TRANSISTOR_OUTPUT], 
    b_word: list[TRANSISTOR_OUTPUT], 
    sel: TRANSISTOR_OUTPUT
) -> list[TRANSISTOR_OUTPUT]:
    '''
    N-bit 2-to-1 Bus Multiplexer.
    Switches an entire multi-bit word (bus) based on a single select signal.
    
    Takes two equal-length lists of bit signals (ordered LSB -> MSB).
    Returns a selected word of equal length.

        a_word[0] ───┐                                 b_word[0] ───┐
                     ├─── [ MUX 0 ] ─── out_word[0]                 ├─── [ MUX 1 ] ─── out_word[1]
        b_word[0] ───┘         │                       b_word[1] ───┘         │
                             Sel                                            Sel

    ============
       EXAMPLE
    ============
    - a_word = [1, 0, 1] (5 in decimal)
    - b_word = [0, 1, 1] (3 in decimal)
    - sel = POWER (1)
    
    - Output:
        - MUX 0: (a[0]=1, b[0]=0, sel=1) -> 0
        - MUX 1: (a[1]=0, b[1]=1, sel=1) -> 1
        - MUX 2: (a[2]=1, b[2]=1, sel=1) -> 1
    - result_word = [0, 1, 1] (Successfully selected b_word)
    '''
    selected_word: list[TRANSISTOR_OUTPUT] = []

    for bit_a, bit_b in zip(a_word, b_word):
        output_bit = mux_2to1(bit_a, bit_b, sel)
        selected_word.append(output_bit)

    return selected_word


def decoder_1to2(a0: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    1-to-2 Decoder.
    Takes 1 input bit (A0) and Outputs 2 lines (Y0, Y1). Either Y0=1 or Y1=1

            A0 ───┬─────────┐
                  │  ┌───┐  └─── [cmos_AND] ─── Y1 (Active when A0=1)
            1 ────┼──┤AND│
                  │  └───┘
                  │  ┌───┐  ┌─── [cmos_NOT] ──┐
                  └──┤AND│──┤                 ├─── Y0 (Active when A0=0)
                     └───┘  └─────────────────┘

    ============
       EXAMPLE
    ============
    - Input: a0 = 0
        - y0 = cmos_NOT(a0) = 1
        - y1 = a0 = 0
        - Returns (y0, y1) = (1, 0)
    - Input: a0 = 1
        - y0 = cmos_NOT(a0) = 0
        - y1 = 1
        - Returns (y0, y1) = (0, 1)
    '''
    y0 = cmos_NOT(a0)
    y1 = a0
    return y0, y1


def decoder_2to4(
    a1: TRANSISTOR_OUTPUT,
    a0: TRANSISTOR_OUTPUT
) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    2-to-4 Decoder.
    Takes 2 input bits (A0, A1) and Outputs 4 lines (Y0, Y1, Y2, Y3). Either Y0=1, Y1=1, Y2=1, Y3=1

        A1 ────┬──────────────┐
               │   ┌─────┐    │
        A0 ────┼───┤ AND ├────┼───────────────> Y0 (00)
               │   └─────┘    │
               │              │   ┌─────┐
               ├──────────────┼───┤ AND ├─────> Y1 (01)
               │              │   └─────┘
               │  (Inv Gates) │   ┌─────┐
               └──────────────┼───┤ AND ├─────> Y2 (10)
                              │   └─────┘
                              │   ┌─────┐
                              └───┤ AND ├─────> Y3 (11)
                                  └─────┘
    ============
       EXAMPLE
    ============
    - Basically we iterate through every combination of 2 bits (00, 01, 10, 11)
    - To do this, we have (a0, a1, ~a0, ~a1)
    - Then we simply assign each of outputs y0,y1,y2,y3 to one of the combinations
        - (a0,a1) --> y0
        - (a0,~a1) --> y1
        - (~a0,a1) --> y2
        - (~a0,~a1) --> y3
    - No matter the combination of a0 and a1, only 1 case will every return 1 by definition
        - Because AND requires both values to be 1, and the NOT guarantees that can only happen in 1 case
    '''
    not_a1 = cmos_NOT(a1)
    not_a0 = cmos_NOT(a0)

    # Calculate active-high lines via minterm AND logic
    y0 = cmos_AND(not_a1, not_a0)
    y1 = cmos_AND(not_a1, a0)
    y2 = cmos_AND(a1, not_a0)
    y3 = cmos_AND(a1, a0)

    return y0, y1, y2, y3


def decoder_3to8(
    a2: TRANSISTOR_OUTPUT, 
    a1: TRANSISTOR_OUTPUT, 
    a0: TRANSISTOR_OUTPUT
) -> tuple[
    TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT,
    TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT
]:
    '''
    3-to-8 Decoder constructed using 2-to-4 logic

                (A1, A0) ───────> [ 2-to-4 Decoder ] ─── (Sub0, Sub1, Sub2, Sub3)
                                        │
                ┌──────────────────────────┴──────────────────────────┐
                ▼                                                     ▼
        A2=0 Branch (Lower)                                  A2=1 Branch (Upper)
        (Y0 = Sub0 AND ~A2)                                  (Y4 = Sub0 AND A2)
        (Y1 = Sub1 AND ~A2)                                  (Y5 = Sub1 AND A2)
        (Y2 = Sub2 AND ~A2)                                  (Y6 = Sub2 AND A2)
        (Y3 = Sub3 AND ~A2)                                  (Y7 = Sub3 AND A2)

    - For 3 inputs, we have 8 possibilities (000, 001, 010, 100, 011, 101, 110, 111)
    - We borrow the same approach from the decoder_2to4, but apply it sequentially instead
    - Idea is: 
        - We first decide which combination of a0 and a1 we are dealing with
            - So decoder_2to4(a1, a0)
            - This gives us (sub0, sub1, sub2, sub3), which can be one of (0001, 0010, 0100, 1000)
        - Then depending on which of these we get, we combine this bit-wise with a2=0 and ~a2=1
            - Suppose we have list[0,0,0,1]
                - list[0,0,0,1] AND a2=0 --> [y0=0, y1=0, y2=0, y3=0]
                - list[0,0,0,1] AND ~a2=1 --> [y4=0, y5=0, y6=0, y7=1]
        - Remember, this works because the output from  `decoder_2to4` is guaranteed to have one and only 1 positive bit 
        - AND a2 is guaranteed to be 0 or 1
    '''
    # Step 1: Decode the two lower bits (A1, A0) into 4 intermediate lines
    sub0, sub1, sub2, sub3 = decoder_2to4(a1, a0)
    not_a2 = cmos_NOT(a2)

    # Step 2: Route to lower 4 outputs (Active when A2 is 0)
    y0 = cmos_AND(sub0, not_a2)
    y1 = cmos_AND(sub1, not_a2)
    y2 = cmos_AND(sub2, not_a2)
    y3 = cmos_AND(sub3, not_a2)

    # Step 3: Route to upper 4 outputs (Active when A2 is 1)
    y4 = cmos_AND(sub0, a2)
    y5 = cmos_AND(sub1, a2)
    y6 = cmos_AND(sub2, a2)
    y7 = cmos_AND(sub3, a2)

    return y0, y1, y2, y3, y4, y5, y6, y7


def comparator_1bit(a: TRANSISTOR_OUTPUT, b: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    1-Bit Magnitude Comparator
    Given two 1-bit inputs (A, B), return a tuple of 1-bit values representing (a_gt_b, a_eq_b, a_lt_b)

            A ───┬──────────────┐
                 │   ┌──────┐   ├─── [cmos_AND] ─── A_GT_B (A=1, B=0)
            B ───┼───┤~B    ├───┘
                 │   └──────┘
                 │   ┌──────┐
                 ├───┤ cmos ├─── A_EQ_B (A == B)
                 │   │ XNOR │
            B ───┼───┤      ├───
                 │   └──────┘
                 │   ┌──────┐
            ~A ──┼───┤ cmos ├─── A_LT_B (A=0, B=1)
            B ───┴───┤ AND  ├───
                     └──────┘
    
    - Intuition
        - a_gt_b = cmos_AND(a, not_b)
            - This works, because if the inversion of B is equal to A, and A = 1, then B must have been 0 to begin with
            - If A were 0, then the AND will return 0 regardless, because 0 cannot be more than anything in binary
        - xor_out = cmos_XOR(a, b), a_eq_b = cmos_NOT(xor_out)
            - This checks because XOR returns 1 if either A or B were 1, but not if they are both 1
            - So if XOR returns 1, they cannot be equal. 
            - Hence, A == B is just the NOT of the XOR
            - This is also known as XNOR
        - a_lt_b = cmos_AND(not_a, b)
            - Same logic as a_gt_b, but in reverse
    
    - (A=0, B=0), (A=1, B=1) => (0, 1, 0)
        - We'll work through the (0,0) case, but the (1,1) case is symmetric
        - ~A = 1, ~B = 1
        - Check if A > B
            - AND(A, ~B) = 0 
        - Check if A == B
            - x1 = XOR(A, B) = 0
            - NOT(x1) = 1
        - Check if A < B
            - AND(~A, B) = 0
    - (A=1, B=0) => (1, 0, 0)
        - ~A = 0, ~B = 1
        - Check if A > B
            - AND(A, ~B) = 1 
        - Check if A == B
            - x1 = XOR(A, B) = 1
            - NOT(x1) = 0
        - Check if A < B
            - AND(~A, B) = 0
    - (A=0, B=1) => (0, 0, 1)
        - ~A = 1, ~B = 0
        - Check if A > B
            - AND(A, ~B) = 0 
        - Check if A == B
            - x1 = XOR(A, B) = 1
            - NOT(x1) = 0
        - Check if A < B
            - AND(~A, B) = 1
    '''
    not_a = cmos_NOT(a)
    not_b = cmos_NOT(b)

    # A > B: A is 1 AND B is 0
    a_gt_b = cmos_AND(a, not_b)

    # A == B: Both are 0 or both are 1 (XNOR)
    xor_out = cmos_XOR(a, b)
    a_eq_b = cmos_NOT(xor_out)

    # A < B: A is 0 AND B is 1
    a_lt_b = cmos_AND(not_a, b)

    return a_gt_b, a_eq_b, a_lt_b


def comparator_nbit(
    a_bits: list[TRANSISTOR_OUTPUT], 
    b_bits: list[TRANSISTOR_OUTPUT]
) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    N-Bit Magnitude Comparator 
    
    - Same as comparator_1bit, returns (a_gt_b, a_eq_b, a_lt_b)
    - When we have multiple bits, we go from the most significant bit (MSB) to least significant bit (LSB)
    - Why?
        - Because for any binary number, the magnitude of MSB strictly dominates the combination of all the less significant bits
        - e.g. 10 > 01, 100 > 011, 1000 > 0111, holds for binary numbers for any size
        - So if MSB_A > MSB_B, it must be true that A > B    
    '''

    # Process from MSB to LSB 
    for bit_a, bit_b in zip(a_bits, b_bits):
        gt, eq, lt = comparator_1bit(bit_a, bit_b)

        if gt:
            return (POWER, GROUND, GROUND)
        elif lt:
            return (GROUND, GROUND, POWER)
        else:
            continue

    return GROUND, POWER, GROUND


def barrel_rotator_right_4bit(
    data: list[TRANSISTOR_OUTPUT], 
    shift_amt: tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    4-Bit Barrel Rotator Right (ROR).
    
    Inputs:
        - 4-bit data list [D0, D1, D2, D3] (MSB -> LSB)
        - 2-bit shift amount tuple [S1, S2] (because 2 bits has 4 combinations)
    
        Returns a rotated 4-bit word

            Data [D0, D1, D2, D3]
                    │
                    ▼
        ┌─────────────────────────┐
        │Stage 0: MUX Bank (1-bit)│ <── S0
        └────────────┬────────────┘
                    │ Intermediate [I0, I1, I2, I3]
                    ▼
        ┌─────────────────────────┐
        │Stage 1: MUX Bank (2-bit)│ <── S1
        └────────────┬────────────┘
                    ▼
        Output [O0, O1, O2, O3]

    - Recall that a 1-bit MUX takes in 2 data inputs, and returns either of them depending on a the control input flag

    - So how do we perform a rotation?
        - Suppose we have [D0,D1,D2,D3], and we want to perform a right rotation of size 3 
        - That just means we want the final state to be [D1,D2,D3,D0]

    - The trick here is entirely how we think about the inputs to `shift_amt`
        - This can be seen as a binary number, representing the number of shifts we require for each input value 
    
    - Since `shift_amt` has $N$ bits, we get from `[D0,D1,D2,D3]` => `[D1,D2,D3,D0]` in N steps!
        - For each of the N steps, we use the binary value for that particular digit of `shift_amt`
        - For example, if `shift_amt` = [1, 1], we perform the right shift in 2 steps
        - Right shift by one step, since the first value is 1, hence 1 * 2^0 --> `[D0,D1,D2,D3]` => `[D3,D0,D1,D2]`
        - Right shift by two steps, since the second value is 1, hence 1 * 2^1 --> `[D3,D0,D1,D2]` => `[D1,D2,D3,D0]`

    - The genius of this stepwise decomposition is that for N control inputs, you can produce shifts of up to 2^N 
    using just mux_2to1
        - If we wanted to do this all at once, we would have needed a mux_4to1 for control input size of N=2
    '''
    s1, s0 = shift_amt
    d0, d1, d2, d3 = data

    # ------------------------------------------------------------------
    # STAGE 0: Shift Right by 0 or 1 position 
    # If s0=0: Keep original [D0, D1, D2, D3]
    # If s0=1: Shift right by 1 -> [D3, D0, D1, D2]
    # ------------------------------------------------------------------
    i0 = mux_2to1(d0, d3, s0) # Wrap-around bit
    i1 = mux_2to1(d1, d0, s0)
    i2 = mux_2to1(d2, d1, s0)
    i3 = mux_2to1(d3, d2, s0)

    # ------------------------------------------------------------------
    # STAGE 1: Shift Right by 2 positions (if s1 is HIGH)
    # If s1=0: Keep Stage 0 output [I0, I1, I2, I3]
    # If s1=1: Shift right by 2 -> [I2, I3, I0, I1] (I0, I1 wrap)
    # ------------------------------------------------------------------
    o0 = mux_2to1(i0, i2, s1) # Wrap-around bit
    o1 = mux_2to1(i1, i3, s1) # Wrap-around bit
    o2 = mux_2to1(i2, i0, s1)
    o3 = mux_2to1(i3, i1, s1)

    return [o0, o1, o2, o3]


def barrel_logical_right_4bit(
    data: list[TRANSISTOR_OUTPUT], 
    shift_amt: tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    4-Bit Barrel Rotator Right (ROR).
        
    Inputs:
        - 4-bit data list [D0, D1, D2, D3] (MSB -> LSB)
        - 2-bit shift amount tuple [S1, S2] (because 2 bits has 4 combinations)

    - The idea is the same as barrel_rotator, in that we are using mux_2to1 N times to perform the rotation, 
    where N=len(shift_amt)
    - However, the difference in that values that go over the edge no longer loop back around. Instead, we replace 
    it with 0

    - So Suppose we have [D0,D1,D2,D3], and we want to perform a right rotation of size 3 
        - That now means we want [0, 0, 0, D0]
        - To do this, let's shift right by 1
            - [D0,D1,D2,D3] => [0,D0,D1,D2] = [i0,i1,i2,i3]
        - Then shift right by 2
            - [0,D0,D1,D2] => [0,0,0,D0]

    '''
    s1, s0 = shift_amt
    d0, d1, d2, d3 = data

    # STAGE 0: Shift by 1 bit (Fill index 3 with GROUND)
    i0 = mux_2to1(d0, GROUND, s0)
    i1 = mux_2to1(d1, d0, s0)
    i2 = mux_2to1(d2, d1, s0)
    i3 = mux_2to1(d3, d2, s0)

    # STAGE 1: Shift by 2 bits (Fill indices 2 & 3 with GROUND)
    o0 = mux_2to1(i0, GROUND, s1)
    o1 = mux_2to1(i1, GROUND, s1)
    o2 = mux_2to1(i2, i0, s1)
    o3 = mux_2to1(i3, i1, s1)

    return [o0, o1, o2, o3]


def half_subtractor(a: TRANSISTOR_OUTPUT, b: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    Computes (a - b) for two single bits.
    Returns (difference, borrow_out).

            A ───┬─────────┐
                 │  ┌───┐  ├─── [cmos_XOR] ─── Difference
            B ───┼──┤XOR│──┘
                 │  └───┘
                 │  ┌───┐  ┌─── [cmos_NOT] ──┐
            ~A ──┼──┤AND│──┤                 ├─── Borrow Out
            B ───┴──└───┘  └─────────────────┘

    - Intuition
        - diff = cmos_XOR(a, b)
            - The diff between A and B is either 1 or 0
            - An XOR will return 1 for (1,0) or (0,1), and 0 otherwise
            - Thus, it measures the diff
        - not_a = cmos_NOT(a=0) = 1
            - Since this does a-b, we need to distinguish between (1,0) and (0,1)
            - The XOR above returns 1 for both, but in the second case, we need to `borrow`
        - borrow = cmos_AND(not_a, b)
            - Since this is AND, the cases (0,0) and (1,0) both set borrow as 0. 
                - This makes sense; if b=0, then we never need to borrow, since we subtract 0
            - In the case (1,1), not_a is set as 0, so borrow is also 0
            - Only in the case (0,1) will we have the situation where AND(not_a, b) = 1
        - The borrow bit is borrowed from the next highest power! So in this case, it is worth 2!

 
    - (a=0, b=0) => (d=0, b=0)
        - diff = cmos_XOR(a=0, b=0) = 0
        - not_a = cmos_NOT(a=0) = 1
        - borrow = cmos_AND(not_a=1, b=0) = 0
        - Output: (diff=0, borrow=0) -> 0 - 0 doesn't need borrowing
    - (a=1, b=0) => (d=1, b=0)
        - diff = cmos_XOR(a=1, b=0) = 1
        - not_a = cmos_NOT(a=1) = 0
        - borrow = cmos_AND(not_a=0, b=0) = 0
        - Output: (diff=1, borrow=0) -> 1 - 0 doesn't need borrowing
    - (a=0, b=1) => (d=1, b=1)
        - diff = cmos_XOR(a=0, b=1) = 1
        - not_a = cmos_NOT(a=0) = 1
        - borrow = cmos_AND(not_a=1, b=1) = 1
        - Output: (diff=1, borrow=1) -> 0 - 1 needs borrowing
        - NOTE: The borrow bit is borrowed from the next highest power, so here it is read as -2+1 = -1
    - (a=1, b=1) => (d=0, b=0)
            - diff = cmos_XOR(a=1, b=1) = 0
            - not_a = cmos_NOT(a=1) = 0
            - borrow = cmos_AND(not_a=0, b=1) = 0
            - Output: (diff=0, borrow=0) -> 1 - 1 doesn't needs borrowing

    '''
    difference = cmos_XOR(a, b)
    not_a = cmos_NOT(a)
    borrow_out = cmos_AND(not_a, b)

    return difference, borrow_out


def full_subtractor(
    a: TRANSISTOR_OUTPUT, 
    b: TRANSISTOR_OUTPUT, 
    b_in: TRANSISTOR_OUTPUT = GROUND
) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    Full Subtractor: Computes (a - b - b_in) considering an incoming Borrow bit

    - Intuition
        - The inputs are read as A - B - B_in
        - For subtraction, order doesn't matter, so hs(a, b) --> hs(a, b_in) is the same either way
        - Remember, every borrow is worth -2!

    - (a=0, b=0, br=0) => (d=0, b=0)
        - hs(a=0, b=0) = d1=0, br1=0
        - hs(d1=0, br=0) = d2=0, br2=0
        - OR(br1=0, br2=0) = br3 = 0
        - Output: d2=0, br3=0
    - (a=0, b=0, br=1) || (a=0, b=1, br=0) => (d=1, b=1)
        - hs(a=0, b=0) = d1=0, br1=0
        - hs(d1=0, br=1) = d2=1, br2=1
        - OR(br1=0, br2=1) = br3 = 1
        - Output: d2=1, br3=1 ==> d2 + br3 = 1 + -2 = -1
    - (a=0, b=1, br=1) => (d=1, b=1)
        - hs(a=0, b=1) = d1=1, br1=1
        - hs(d1=1, br=1) = d2=0, br2=0
        - OR(br1=1, br2=0) = br3 = 1
        - Output: d2=0, br3=1 ==> d2 + br3 = 0 + -2 = -2
    - (a=1, b=1, br=0) || (a=1, b=0, br=1) => (d=0, b=0)
        - hs(a=1, b=1) = d1=0, br1=0
        - hs(d1=0, br=0) = d2=0, br2=0
        - OR(br1=0, br2=0) = br3 = 0
        - Output: d2=0, br3=0 ==> d2 + br3 = 0 + 0 = 0
    - (a=1, b=1, br=1) => (d=1, b=1)
        - hs(a=1, b=1) = d1=0, br1=0
        - hs(d1=0, br=1) = d2=1, br2=1
        - OR(br1=0, br2=1) = br3 = 1
        - Output: d2=1, br3=1 ==> d2 + br3 = 1 + -2 = -1
    - (a=1, b=0, br=0) => (d=1, b=0)
        - hs(a=1, b=0) = d1=1, br1=0
        - hs(d1=1, br=0) = d2=1, br2=0
        - OR(br1=0, br2=0) = br3 = 0
        - Output: d2=1, br3=0 ==> d2 + br3 = 1 + 0 = 1
    '''
    diff1, borrow1 = half_subtractor(a, b)
    final_diff, borrow2 = half_subtractor(diff1, b_in)
    final_borrow = cmos_OR(borrow1, borrow2)

    return final_diff, final_borrow


def array_multiplier_4bit(
    a_bits: list[TRANSISTOR_OUTPUT], 
    b_bits: list[TRANSISTOR_OUTPUT]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    Multiplier that takes in 4 bit values for inputs A and B

    Inputs:
        - a_bits: 4-bit multiplicand [A0, A1, A2, A3] (MSB -> LSB)
        - b_bits: 4-bit multiplier   [B0, B1, B2, B3] (MSB -> LSB)
    Returns:
        - 8-bit product [P0, P1, P2, P3, P4, P5, P6, P7] (MSB -> LSB)

    - Since both numbers are 4 bits, it is impossible for any product to exceed 8 bits
        - (2^4 - 1)^2 = 2^8 - 2^5 + 1 < 2^8
        - This is why I can guarantee that output is 8 bits
    
    ============
    EXAMPLE (3 x 5 = 15)
    ============
    - a_bits = [0, 0, 1, 1] (Decimal 3)
    - b_bits = [0, 1, 0, 1] (Decimal 5)
    - Output = [0, 0, 0, 0, 1, 1, 1, 1]

    
    First we produce a 4x4 matrix, where a row is every a_bit multiplied by a fixed b_bit.

    Suppose:
        - a_bits = [0, 0, 1, 1] 3
        - b_bits = [0, 1, 1, 0] 6
        - Then we have:
            - [0*0, 0*0, 1*0, 1*0] (0011 * 0) = [0, 0, 0, 0]
            - [0*1, 0*1, 1*1, 1*1] (0011 * 1) = [0, 0, 1, 1]
            - [0*1, 0*1, 1*1, 1*1] (0011 * 1) = [0, 0, 1, 1]
            - [0*0, 0*0, 1*0, 1*0] (0011 * 0) = [0, 0, 0, 0]

        - Next, we want to add these rows together
            - Keep in mind, however, that each b bit does not have the same value
            - In the first row `(0011 * 0)`, the b_bit has value 2^0 = 1
            - In the second row `(0011 * 1)`, the b_bit has value 2^1 = 2
            - etc
        
        - THEREFORE, when we add row 1 and row 2 (for example), we cannot just do 0000 + 0011
            - This is because 0011 is multiplied by 2^1
            - Consequently, it is shifted leftwards by 1
            - So 0011 is actually 00110
            - Think about it: when you multiple 3 by the 1 in the 2^1 position, we are actually doing 3*2, not 3*1. Therefore, when we shift left, 
            we are simply multiplying that value by 2

        - So the final sum of the matrix is actually 
            - [0,0,0,0,0] + [0,0,1,1,0] = [0,0,1,1,0] (0 + 6 = 6)
            - [0,0,0,1,1,0] + [0,0,1,1,0,0] = [0,1,0,0,1,0] (6 + 12 = 18)
            - [0,0,1,0,0,1,0] + [0,0,0,0,0,0,0] = [0,0,1,0,0,1,0] (18 + 0 = 18)
    '''
    
    partial_products = [
        [cmos_AND(a, b) for a in a_bits]
        for b in reversed(b_bits)
    ]

    result = [0] * 8
    for i, row in enumerate(partial_products):
        ## Pad rows to 8 bits since that is the maximum bits from the product of two 4 bit numbers
        padded_row = ([0]*(4-i)) + row + ([0]*i)
        
        # Accumulate using gate-level addition. ripple_carry_adder is LSB-first; rows here are MSB-first
        sum_bits, _ = ripple_carry_adder(result[::-1], padded_row[::-1])
        result = sum_bits[::-1]
        
    return result


def binary_encoder_4to2(
    inputs: list[TRANSISTOR_OUTPUT]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    4-to-2 Binary Encoder
    
    Inputs (MSB -> LSB):
        - inputs: [I3, I2, I1, I0]
        - EXACTLY ONE input is 1, everything else is 0
    Returns:
        - encoded_bits: [Y1, Y0] (MSB -> LSB)

    Truth Table:
        I3  I2  I1  I0 | Y1  Y0
        -----------------------
         0   0   0   1 |  0   0
         0   0   1   0 |  0   1
         0   1   0   0 |  1   0
         1   0   0   0 |  1   1


    - If [i3=0, i2=0, i1=0, i0=1]
        - y1 = OR(i3, i2) = OR(0, 0) = 0
        - y0 = OR(i3, i1) = OR(0, 0) = 0
        - Therefore [y1=0, y0=0]
    - If [i3=0, i2=0, i1=1, i0=0]
        - y1 = OR(i3, i2) = OR(0, 0) = 0
        - y0 = OR(i3, i1) = OR(0, 1) = 1
        - Therefore [y1=0, y0=1]
    - If [i3=0, i2=1, i1=0, i0=0]
        - y1 = OR(i3, i2) = OR(0, 1) = 1
        - y0 = OR(i3, i1) = OR(0, 0) = 0
        - Therefore [y1=1, y0=0]
    - If [i3=1, i2=0, i1=0, i0=0]
        - y1 = OR(i3, i2) = OR(1, 0) = 1
        - y0 = OR(i3, i1) = OR(1, 0) = 1
        - Therefore [y1=1, y0=1]
    '''
    i3, i2, i1, i0 = inputs

    # Output Y1 = I3 OR I2
    y1 = cmos_OR(i3, i2)

    # Output Y0 = I3 OR I1
    y0 = cmos_OR(i3, i1)

    return [y1, y0]


def priority_encoder_4to2(
    inputs: list[TRANSISTOR_OUTPUT]
) -> tuple[list[TRANSISTOR_OUTPUT], TRANSISTOR_OUTPUT]:
    '''
    4-to-2 Priority Encoder
    Priorities: I3 (Highest) > I2 > I1 > I0 (Lowest)
    
    Inputs (MSB -> LSB):
        - inputs: [I3, I2, I1, I0]
    Returns:
        - encoded_bits: [Y1, Y0] (MSB -> LSB)
        - valid: POWER if at least one input is HIGH, GROUND otherwise

    Truth Table:
        I3  I2  I1  I0 | Y1  Y0 | V
        ---------------------------
         0   0   0   0 |  X   X | 0
         0   0   0   1 |  0   0 | 1
         0   0   1   X |  0   1 | 1
         0   1   X   X |  1   0 | 1
         1   X   X   X |  1   1 | 1

    Logic Equations:
        - Y1 = I3 OR I2
        - Y0 = I3 OR (NOT(I2) AND I1)
        - V  = I3 OR I2 OR I1 OR I0
    '''
    i3, i2, i1, i0 = inputs

    # Assert that at least one value is 1, else return invalid return
    v_01 = cmos_OR(i0, i1)
    v_23 = cmos_OR(i2, i3)
    valid = cmos_OR(v_01, v_23)
    if not valid:
        return [GROUND, GROUND], valid

    valid = POWER
    if i3:
        return [POWER, POWER], valid
    elif i2:
        return [POWER, GROUND], valid
    elif i1:
        return [GROUND, POWER], valid
    elif i0:
        return [GROUND, GROUND], valid


def adder_subtractor_4bit(
    a_bits: list[TRANSISTOR_OUTPUT], 
    b_bits: list[TRANSISTOR_OUTPUT], 
    is_subtraction: TRANSISTOR_OUTPUT
) -> tuple[list[TRANSISTOR_OUTPUT], TRANSISTOR_OUTPUT]:
    '''
    Using the two's complement definition of binary values, we can create a unified gate that does both 
    addition and subtraction

             A_bits        B_bits
               │             │
               │        ┌────┴────┐
               │        │ XOR Gate│ <── sub control signal
               │        └────┬────┘
               ▼             ▼
          ┌───────────────────────┐
          │  Ripple Carry Adder   │ <── c_in = sub
          └──────────┬────────────┘
                     ▼
             Result (Sum / Diff)

    ============
       EXAMPLE
    ============
    - a_bits = [0, 0, 1, 1] = 3, b_bits = [1, 1, 1, 0] = -2, is_subtraction = POWER
        - 3 - -2 = 5
        - inverted_or_same_b = [0, 0, 0, 1] = 1
        - [0, 0, 1, 1] + [0, 0, 0, 1] + [0, 0, 0, 1] = [0, 1, 0, 1] = 5
    
    - a_bits = [0, 1, 1, 1] = 7, b_bits = [1, 0, 1, 1] = -5, is_subtraction = GROUND
        - inverted_or_same_b = [1, 0, 1, 1] = -5
        - [0, 1, 1, 1] + [1, 0, 1, 1] = [1, 0, 0, 1, 0] == truncated ==> [0, 0, 1, 0] = 2

    '''
    # Step 1: Conditionally invert b_bits using XOR
    inverted_or_same_b: list[TRANSISTOR_OUTPUT] = []
    for bit in b_bits:
        ## Inversion via XOR; 
        ##    - when is_subtraction = 1, bit = 1 --> 0, is_subtraction = 1, bit = 0 --> 1
        ##    - when is_subtraction = 0, bit = 1 --> 1, is_subtraction = 0, bit = 0 --> 0
        inverted_or_same = cmos_XOR(bit, is_subtraction)
        inverted_or_same_b.append(inverted_or_same)

    # Step 2: Run through standard ripple carry adder, using sub as initial carry_in!
    result_bits: list[TRANSISTOR_OUTPUT] = []
    carry = is_subtraction

    for bit_a, bit_b in zip(reversed(a_bits), reversed(inverted_or_same_b)):
        s, carry = full_adder(bit_a, bit_b, carry)
        # Walking LSB -> MSB, so prepend to keep the result MSB-first
        result_bits.insert(0, s)

    return result_bits, carry


def alu_4bit(
    a_bits: list[TRANSISTOR_OUTPUT], 
    b_bits: list[TRANSISTOR_OUTPUT], 
    opcode: tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]
) -> tuple[list[TRANSISTOR_OUTPUT], dict[str, TRANSISTOR_OUTPUT]]:
    '''
    4-Bit Arithmetic Logic Unit (ALU)
    
    Inputs:
        - a_bits: 4-bit word [A3, A2, A1, A0] (MSB -> LSB)
        - b_bits: 4-bit word [B3, B2, B1, B0] (MSB -> LSB)
        - opcode: 3-bit selection signal (op2, op1, op0)
        
    Outputs:
        - result: 4-bit word output
        - flags: Dictionary containing status flags (Zero, Sign, Carry, Overflow)

            A_bits ─────────┬──────────────┬──────────────┬──────────────┐
            B_bits ──────┐  │              │              │              │
                         ▼  ▼              ▼              ▼              ▼
                    ┌─────────┐      ┌───────────┐  ┌───────────┐  ┌───────────┐
                    │ Adder / │      │ Bitwise   │  │ Bitwise   │  │ Barrel    │
                    │ Subtr.  │      │ Logic     │  │ Logic     │  │ Rotator   │
                    └────┬────┘      └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
                         │                 │              │              │
                         ▼                 ▼              ▼              ▼
                    ──────────────────────────────────────────────────────────
                                 8-to-1 4-Bit MUX (Opcode Select)
                    ──────────────────────────┬───────────────────────────────
                                              │
                                              ▼
                                       4-Bit Result
                                              │
                                              ├───────────► Status Flags
                                              │             (Zero, Sign, Carry, Overflow)
                                              ▼
    '''
    op2, op1, op0 = opcode

    ## Check that inputs are 4 bits
    assert(len(a_bits) == 4) 
    assert(len(b_bits) == 4)

    # ------------------------------------------------------------------
    # 1. PARALLEL EXECUTION OF ALL OPERATIONS
    # ------------------------------------------------------------------

    # Bitwise Logic Operations (4/8 operations covered)
    and_result = [cmos_AND(a, b) for a, b in zip(a_bits, b_bits)]
    or_result  = [cmos_OR(a, b)  for a, b in zip(a_bits, b_bits)]
    xor_result = [cmos_XOR(a, b) for a, b in zip(a_bits, b_bits)]
    not_result = [cmos_NOT(a) for a in a_bits]

    # Arithmetic Operations (ADD / SUB via Two's Complement) (6/8 operations covered)
    arith_result, carry_out = adder_subtractor_4bit(a_bits, b_bits, is_subtraction=op0)
    
    # Shift / Rotate Operation (Use lower 2 bits of B as shift amount) (7/8 operations covered)
    shift_amt = (b_bits[2], b_bits[3])
    ror_result = barrel_rotator_right_4bit(a_bits, shift_amt)

    # Comparison Operation (Format [0, 0, A_GT_B, A_EQ_B]) (8/8 operations covered)
    gt, eq, lt = comparator_nbit(a_bits, b_bits)
    cmp_result = [GROUND, GROUND, gt, eq]

    # ------------------------------------------------------------------
    # 2. MULTIPLEXING RESULTS (Selecting via Opcode)
    # ------------------------------------------------------------------
    # Iterate over opcode to narrow down the result to return
    
    # Stage 0: Select based on op0 (LSB)
    stage0_0 = n_bit_mux_2to1(arith_result, arith_result, op0)  # 000 vs 001 (ADD vs SUB)
    stage0_1 = n_bit_mux_2to1(and_result,   or_result,    op0)  # 010 vs 011 (AND vs OR)
    stage0_2 = n_bit_mux_2to1(xor_result,   not_result,   op0)  # 100 vs 101 (XOR vs NOT)
    stage0_3 = n_bit_mux_2to1(ror_result,   cmp_result,   op0)  # 110 vs 111 (ROR vs CMP)

    # Stage 1: Select based on op1 (Middle bit)
    stage1_0 = n_bit_mux_2to1(stage0_0, stage0_1, op1)         # (000/001) vs (010/011)
    stage1_1 = n_bit_mux_2to1(stage0_2, stage0_3, op1)         # (100/101) vs (110/111)

    # Stage 2: Select based on op2 (MSB) -> Final 4-bit Result
    result = n_bit_mux_2to1(stage1_0, stage1_1, op2)

    # ------------------------------------------------------------------
    # 3. STATUS FLAG GENERATION (IF ANY)
    # ------------------------------------------------------------------
    # Zero Flag (Z): Returns 1 if all result bits are 0 (NOR logic across all bits)
    nor_01 = cmos_NOR(result[0], result[1])
    nor_23 = cmos_NOR(result[2], result[3])
    zero_flag = cmos_AND(nor_01, nor_23)

    # Sign Flag (S): Equal to MSB (bit 0 in MSB-first array)
    sign_flag = result[0]

    # Carry Flag (C): Active only for ADD/SUB operations
    is_arithmetic = cmos_AND(cmos_NOT(op2), cmos_NOT(op1))
    carry_flag = cmos_AND(carry_out, is_arithmetic)

    # Overflow Flag (V): Signed overflow occurs when two numbers of same sign 
    # produce a result of opposite sign.
    # Formula: V = (A_msb == B_msb) AND (A_msb != Result_msb)
    a_msb, b_msb, r_msb = a_bits[0], b_bits[0], result[0]
    # For SUB, B's effective sign is inverted
    b_eff_msb = cmos_XOR(b_msb, op0) 
    same_input_sign = cmos_NOT(cmos_XOR(a_msb, b_eff_msb))
    diff_result_sign = cmos_XOR(a_msb, r_msb)
    overflow_flag = cmos_AND(cmos_AND(same_input_sign, diff_result_sign), is_arithmetic)

    flags = {
        "ZERO": zero_flag,
        "SIGN": sign_flag,
        "CARRY": carry_flag,
        "OVERFLOW": overflow_flag
    }

    return result, flags


# ------------------------------ 4_stateless_to_stateful_ops.ipynb

def sr_latch(set: TRANSISTOR_OUTPUT, reset: TRANSISTOR_OUTPUT, val_prev: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    The purpose of an SR Latch is to allow us to persist the state of 1 bit of information. Let's call this `val`.
    
    To do this, we take in 3 inputs:
        - A `set` signal, indicating whether we should set `val` to 1
        - A `reset` signal, indicating whether we should set `val` to 0
        - The previous value held by `val`, which call `val_prev`
        - Note that in an SR Latch, `set` and `reset` must not both be 1 at the same time. 
    
    Using these, the SR latch outputs a value of `val`, and its inverse `val_prime`
        - Note that though `val_prime` is the inverse of `val`, it is not derived by passing `val` through a NOT gate
        - Instead, `val_prime` is computed separately, to ensure that there is no delay between the output `val` and `val_prime` being emitted
    
    The truth table below shows how the SR Latch turns the inputs into persistent byte value storage.
        - However, keep in mind that this doesn't always happen in one pass!
        - Sometimes, we can end up with intermediate val/val_prime values that require a few steps for its value to settle
        - We will show these in the truth table below

    Truth Table / Trace:
        - val_prev = 0 (val_prime_prev = 1):

            - set = 0, reset = 0 (HOLD STATE): Neither set nor reset. We want the circuit to output the same `val` it already has
                - Pass 1: val_prime = NOR(set=0, val_prev=0) = 1
                - Pass 1: val = NOR(reset=0, val_prime=1) = 0
                - Settled: (val=0, val_prime=1)

            - set = 0, reset = 1 (RESET STATE): Reset state. But since val = 0 already, we continue to output val = 0
                - Pass 1: val_prime = NOR(set=0, val_prev=0) = 1
                - Pass 1: val = NOR(reset=1, val_prime=1) = 0
                - Settled: (val=0, val_prime=1)

            - set = 1, reset = 0 (SET STATE): Set state.
                - Pass 1: val_prime = NOR(set=1, val_prev=0) = 0
                - Pass 1: val = NOR(reset=0, val_prime=0) = 1
                - +++++++++++++++++++++++++++++++++++++++++++++++++
                - Pass 2: val_prime = NOR(set=1, val=1) = 0
                - Pass 2: val = NOR(reset=0, val_prime=0) = 1
                - +++++++++++++++++++++++++++++++++++++++++++++++++                
                - Settled: (val=1, val_prime=0)

        - val_prev = 1 (val_prime_prev = 0):

            - set = 0, reset = 0 (HOLD STATE):
                - Pass 1: val_prime = NOR(set=0, val_prev=1) = 0
                - Pass 1: val = NOR(reset=0, val_prime=0) = 1
                - Settled: (val=1, val_prime=0)

            - set = 0, reset = 1 (RESET STATE):
                - Pass 1: val_prime = NOR(set=0, val_prev=1) = 0
                - Pass 1: val = NOR(reset=1, val_prime=0) = 0
                - +++++++++++++++++++++++++++++++++++++++++++++++++
                - Pass 2: val_prime = NOR(set=0, val=0) = 1
                - Pass 2: val = NOR(reset=1, val_prime=1) = 0
                - +++++++++++++++++++++++++++++++++++++++++++++++++
                - Settled: (val=0, val_prime=1)

            - set = 1, reset = 0 (SET STATE):
                - Pass 1: val_prime = NOR(set=1, val_prev=1) = 0
                - Pass 1: val = NOR(reset=0, val_prime=0) = 1
                - Settled: (val=1, val_prime=0)
    '''
    if set == 1 and reset == 1:
        raise ValueError("Invalid State: 'set' and 'reset' cannot both be 1.")

    val = val_prev
    val_prime = 0 if val_prev == 1 else 1

    # Loop until the cross-coupled NOR gates stabilize into equilibrium
    prev_state = None
    while (val, val_prime) != prev_state:
        prev_state = (val, val_prime)

        # Gate 1: Drives val_prime using external 'set' and internal feedback 'val'
        val_prime = cmos_NOR(set, val)

        # Gate 2: Drives val using external 'reset' and internal feedback 'val_prime'
        val = cmos_NOR(reset, val_prime)

    return val, val_prime


def d_latch(setval: TRANSISTOR_OUTPUT, enable: TRANSISTOR_OUTPUT, val_prev: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    Similar to SR Latch, the D latch is designed to handle the persistence of 1 bit of data. 
    In fact, the D latch LITERALLY contains an SR Latch, just with better UI to avoid mistakes with the inputs.

    Inputs   
        - `setval`
            - Unlike the SR latch, which uses 1 input for `setval` and 1 for `reset`, the D Latch only takes 1 input for both. 
            - If the input is 1, it signals `setval`. Else, it signals `reset`
            - This avoids the possibility of having both setval=1 and reset=1, which was the problem with the SR latch setup
        - `enable`
            - An extra gate that determines whether the `setval` input is passed foward
            - If `enable = 0`, `setval` is always ignored, no matter its value
        - `val_prev`
            - `val` from previous time step
    '''
    reset = cmos_NOT(setval)
    
    setval = cmos_AND(setval, enable)
    reset = cmos_AND(reset, enable)
    
    return sr_latch(setval, reset, val_prev)


def d_flip_flop(input: TRANSISTOR_OUTPUT, enable: TRANSISTOR_OUTPUT, slave_val_prev: TRANSISTOR_OUTPUT, master_val_prev: TRANSISTOR_OUTPUT) -> tuple[TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT, TRANSISTOR_OUTPUT]:
    '''
    Rising-Edge Triggered Master-Slave D Flip-Flop.
    
    Inputs:
        - input Input data bit
        - enable: From system clock signal
        - slave_val_prev: Stored output Q (from Slave)
        - master_val_prev: Stored intermediate state Q (from Master)
        
    Returns:
        - (Q, Q_bar, master_Q): Updated output Q, inverse Q_bar, and new internal Master Q state
    '''
    not_enable = cmos_NOT(enable)
    
    # Stage 1: Master Latch (Enabled when Clock is LOW)
    master_q, _ = d_latch(input, not_enable, master_val_prev)
    
    # Stage 2: Slave Latch (Enabled when Clock is HIGH)
    slave_q, not_slave_q = d_latch(master_q, enable, slave_val_prev)
    
    return slave_q, not_slave_q, master_q


def n_bit_register(
    inputs: list[TRANSISTOR_OUTPUT], 
    enable: TRANSISTOR_OUTPUT, 
    load: TRANSISTOR_OUTPUT, 
    slave_vals_prev: list[TRANSISTOR_OUTPUT], 
    master_vals_prev: list[TRANSISTOR_OUTPUT]
) -> tuple[list[TRANSISTOR_OUTPUT], list[TRANSISTOR_OUTPUT], list[TRANSISTOR_OUTPUT]]:
    '''
    N-Bit Synchronous Register with Load Enable using Master-Slave D Flip-Flops.
    
    Inputs:
        - inputs: List of N input data bits
        - enable: System clock signal
        - load: Control signal (1 = load new input on tick, 0 = hold current Q)
        - slave_vals_prev: List of N stored output bits (from Slaves)
        - master_vals_prev: List of N stored intermediate bits (from Masters)
        
    Returns:
        - (outputs, not_outputs, new_master_states): Tuple of outputs Q, ~Q, and internal Master states
    '''
    n = len(inputs)
    outputs = [0] * n
    not_outputs = [0] * n
    new_master_states = [0] * n
    
    for i in range(n):
        # MUX selects between external input bus (load=1) and recirculating Q (load=0)
        d_in = mux_2to1(d0=slave_vals_prev[i], d1=inputs[i], sel=load)
        
        # Execute Master-Slave D Flip-Flop
        slave_q, not_slave_q, master_q = d_flip_flop(
            input=d_in, 
            enable=enable, 
            slave_val_prev=slave_vals_prev[i], 
            master_val_prev=master_vals_prev[i]
        )
        
        outputs[i] = slave_q
        not_outputs[i] = not_slave_q
        new_master_states[i] = master_q
        
    return outputs, not_outputs, new_master_states


def read_port_4xN(
    slave_state_matrix: list[list[TRANSISTOR_OUTPUT]],  # 4 x N stored outputs
    read_addr: list[TRANSISTOR_OUTPUT]                  # 2-bit address [A1, A0]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    One read port: N 4-to-1 MUXes side by side, sharing the same select lines.
    Bit i of the output is bit i of the register that read_addr points at.

    It reads the stored outputs (Q) and has no clock input, so it returns
    whatever the registers held when it was called.
    '''
    return [
        mux_4to1(q0, q1, q2, q3, sel=read_addr)
        for q0, q1, q2, q3 in zip(*slave_state_matrix)
    ]


def register_file_4xN(
    write_data: list[TRANSISTOR_OUTPUT],
    write_addr: list[TRANSISTOR_OUTPUT],   # 2-bit address [A1, A0]
    read_addr_a: list[TRANSISTOR_OUTPUT],  # 2-bit address [A1, A0]
    read_addr_b: list[TRANSISTOR_OUTPUT],  # 2-bit address [A1, A0]
    write_enable: TRANSISTOR_OUTPUT,       # Global LOAD signal
    enable: TRANSISTOR_OUTPUT,             # System Clock (CLK)
    slave_state_matrix: list[list[TRANSISTOR_OUTPUT]],   # 4 x N stored outputs
    master_state_matrix: list[list[TRANSISTOR_OUTPUT]]   # 4 x N intermediate states
) -> tuple[list[TRANSISTOR_OUTPUT], list[TRANSISTOR_OUTPUT], list[list[TRANSISTOR_OUTPUT]], list[list[TRANSISTOR_OUTPUT]]]:
    '''
    4-Register Addressable Register File (4 words of N-bits each), with two read ports.

    Inputs:
        - write_data: N-bit input data bus
        - write_addr: 2-bit binary write selection
        - read_addr_a, read_addr_b: 2-bit binary read selection for Port A and Port B
        - write_enable: Master LOAD line
        - enable: System clock signal
        - slave_state_matrix: 4xN array holding stored outputs for all 4 registers
        - master_state_matrix: 4xN array holding intermediate states for all 4 registers

    Returns:
        - (read_data_a, read_data_b, new_slave_matrix, new_master_matrix)
        - Both read ports return the values stored before this call. A write to the
          register being read shows up on the next call.
    '''
    # Step 1: Read both ports from the stored state, before any register updates
    read_data_a = read_port_4xN(slave_state_matrix, read_addr_a)
    read_data_b = read_port_4xN(slave_state_matrix, read_addr_b)

    # Step 2: Decode 2-bit Write Address into 4 Word Lines (W0..W3)
    word_lines = decoder_2to4(*write_addr)

    new_slave_matrix = []
    new_master_matrix = []

    # Step 3: Process all 4 Registers in Parallel
    for r in range(4):
        # Register r receives LOAD = 1 ONLY if write_enable is active AND its Word Line is active
        reg_load = cmos_AND(write_enable, word_lines[r])

        # Execute N-Bit Register for Row r
        outputs, _, master_states = n_bit_register(
            inputs=write_data,
            enable=enable,
            load=reg_load,
            slave_vals_prev=slave_state_matrix[r],
            master_vals_prev=master_state_matrix[r]
        )

        new_slave_matrix.append(outputs)
        new_master_matrix.append(master_states)

    return read_data_a, read_data_b, new_slave_matrix, new_master_matrix


def decoder_4to16(
    a3: TRANSISTOR_OUTPUT,
    a2: TRANSISTOR_OUTPUT,
    a1: TRANSISTOR_OUTPUT,
    a0: TRANSISTOR_OUTPUT
) -> tuple[TRANSISTOR_OUTPUT, ...]: ##tuple of len 16
    '''
    4-to-16 Decoder built from two 2-to-4 decoders.
    Output line 4*h + l is on only when high line h and low line l are both on.
    '''
    high = decoder_2to4(a3, a2) ## 4 outcomes, [1,0,0,0], [0,1,0,0] ...
    low = decoder_2to4(a1, a0) ## 4 outcomes
    return tuple(cmos_AND(h, l) for h in high for l in low) ## 4 * 4 = 16 outcomes


def mux_16to1(
    data: list[TRANSISTOR_OUTPUT], ##list of len 16
    sel: list[TRANSISTOR_OUTPUT] ##list of len 4, representing the 2^4 possible values 
) -> TRANSISTOR_OUTPUT:
    '''
    16-to-1 MUX built from five 4-to-1 MUXes.

    Inputs:
        - data: 16 data lines [D0 .. D15]
        - sel: 4-bit select [S3, S2, S1, S0] (MSB -> LSB)
    '''
    ## Get selector bits
    s3, s2, s1, s0 = sel 

    # `data` has length 16. Split it into 4 parts, and use (s0,s1) to select 1 of 4 bits in each part
    group_outputs = [mux_4to1(*data[4 * g: 4 * g + 4], sel=(s1, s0)) for g in range(4)]

    # `group_outputs` has 4 bits. Use (s2, s3) to select the 1 of 4 bits from it
    return mux_4to1(*group_outputs, sel=(s3, s2))


def ram_16xN(
    write_data: list[TRANSISTOR_OUTPUT],
    addr: list[TRANSISTOR_OUTPUT],      # 4-bit address [A3, A2, A1, A0]
    write_enable: TRANSISTOR_OUTPUT,
    enable: TRANSISTOR_OUTPUT,          # System Clock (CLK)
    slave_state_matrix: list[list[TRANSISTOR_OUTPUT]],   # 16 x N stored outputs
    master_state_matrix: list[list[TRANSISTOR_OUTPUT]]   # 16 x N intermediate states
) -> tuple[list[TRANSISTOR_OUTPUT], list[list[TRANSISTOR_OUTPUT]], list[list[TRANSISTOR_OUTPUT]]]:
    '''
    16-word RAM, N bits per word. One address for both read and write.

    Inputs:
        - write_data: N-bit word to store
        - addr: 4-bit address
        - write_enable: 1 = store write_data at addr on the rising edge
        - enable: System clock signal
        - slave_state_matrix / master_state_matrix: 16 x N state for all words

    Returns:
        - (read_data, new_slave_matrix, new_master_matrix)
        - read_data is the word stored at addr before this call
    '''
    # Read the previous `word` stored at `addr`, before any register updates
    read_data: list[TRANSISTOR_OUTPUT] = [mux_16to1(list(column), addr) for column in zip(*slave_state_matrix)]

    # Get the bit-mask for the address of the word from `addr`. Remember that decoder_4to16 outputs a 
	# list of length 16 with 1 bit of 1 value, and 15 bits of 0 value
    word_lines: list[TRANSISTOR_OUTPUT] = decoder_4to16(*addr)

    new_slave_matrix = []
    new_master_matrix = []

    # Step 3: Only the addressed word loads, and only when write_enable is on
    for w in range(16):
        word_load = cmos_AND(write_enable, word_lines[w])

        outputs, _, master_states = n_bit_register(
            inputs=write_data,
            enable=enable,
            load=word_load,
            slave_vals_prev=slave_state_matrix[w],
            master_vals_prev=master_state_matrix[w]
        )

        new_slave_matrix.append(outputs)
        new_master_matrix.append(master_states)

    return read_data, new_slave_matrix, new_master_matrix


def rom_16xN(
    rom_contents: list[list[TRANSISTOR_OUTPUT]],
    addr: list[TRANSISTOR_OUTPUT]   # 4-bit address [A3, A2, A1, A0]
) -> list[TRANSISTOR_OUTPUT]:
    '''
    16-word ROM, N bits per word. No clock and no write port.

    Inputs:
        - rom_contents: up to 16 words, each an MSB-first list of N bits. Words past the end read as 0
        - addr: 4-bit address

    Returns:
        - The N-bit word stored at addr
    '''
    assert 1 <= len(rom_contents) <= 16, 'ROM holds 1 to 16 words'

    word_lines = decoder_4to16(*addr)
    n_bits = len(rom_contents[0])

    read_data = []
    for bit in range(n_bits):
        # Bit line: OR of every word line wired to it (every word with a 1 in this position)
        bit_line = GROUND
        for word, word_bits in enumerate(rom_contents):
            if word_bits[bit]:
                bit_line = cmos_OR(bit_line, word_lines[word])
        read_data.append(bit_line)

    return read_data


def int_to_bits(value: int, width: int) -> list[TRANSISTOR_OUTPUT]:
    '''
	Given `value`, return its binary representation as a list from left to right

	Example:
		- Suppose value = 10, width = 4
		- 10's binary value is `1010`
		- When i = 0
			- width - 1 - i = 3
			- value >> 3 ===> `1010` >> 3 ===> `0001`
			- Therefore, (value >> 3) & 1 is just `0001` & `0001` = `0001`, which is just 1
			- First value returns 1
		- When i = 1
			- width - 1 - i = 2
			- value >> 2 ===> `1010` >> 2 ===> `0010`
			- Therefore, (value >> 2) & 1 is just `0010` & `0001` = `0000`, which is just 0
			- Second value returns 0
		- etc.
		- End with [1, 0, 1, 0]
	'''
    return [POWER if (value >> (width - 1 - i)) & 1 else GROUND for i in range(width)]


def bits_to_int(bits: list[TRANSISTOR_OUTPUT]) -> int:
    '''
	Given a list of bits, convert it back to an integer

	Example:
		- Suppose bits = [1, 0, 1, 0]
		- Then we loop from MSB -> LSB
		- Init value = 0
		- First bit is 1
			- value = 0*2 + (1 if bit else 0) = 1
		- Second bit is 0
			- value = 1*2 + (1 if bit else 0) = 2
		- Third bit is 1
			- value = 2*2 + (1 if bit else 0) = 5
		- Fourth bit is 0
			- value = 5*2 + (1 if bit else 0) = 10

	Note: The approach used here is known as Horner's method, and is derived via 
	factorisation to avoid exponents
		- Option 1: b1 * 2**3 + b2 * 2**2 + b3 * 2**1 + b4 * 2**0
		- Option 2: ((b1 * 2 + b2) * 2 + b3) * 2 + b4
	
	'''
    value = 0
    for bit in bits:
        value = value * 2 + (1 if bit else 0)
    return value


def power_on_state(n_words: int, n_bits: int) -> dict[str, list[list[TRANSISTOR_OUTPUT]]]:
    '''
    Starting states of slave and master when clock starts up.

	Suppose we create 3 words, each with 4 bits. Then the starting state of both slave and
	master are:
		- slave: [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		- master: [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    '''
    # Built row by row, so no two rows are the same list object
    return {
        'slave': [[GROUND] * n_bits for _ in range(n_words)],
        'master': [[GROUND] * n_bits for _ in range(n_words)],
    }


State = dict[str, Any]


Outputs = Any


StepFn = Callable[[TRANSISTOR_OUTPUT, State], tuple[Outputs, State]]


def clock_cycle(step: StepFn, state: State):
    '''
    Run one full clock cycle: CLK = 0, then CLK = 1.

    Inputs:
        - step: function (clk, state) -> (outputs, new_state), wrapping one component call
        - state: the component's current state

    Returns:
        - (outputs, new_state): outputs from the CLK = 1 half, and the state after the rising edge
    '''
    ## By convention, nothing happens when going from 1 --> 0
    _, new_state = step(GROUND, state) 

	## We get new outputs when 0 --> 1, so store and return
    outputs, new_state = step(POWER, new_state)
    return outputs, new_state


def two_register_chain(clk, state, a_input):
    '''
    Load `a_input` every cycle. 
	
	Register B loads A's output every cycle.
    '''
    a_out, _, a_master = n_bit_register(
		a_input, 
		clk, 
		POWER, 
		state['A']['slave'][0], 
		state['A']['master'][0]
	)
    b_out, _, b_master = n_bit_register(
		a_out, 
		clk, 
		POWER, 
		state['B']['slave'][0], 
		state['B']['master'][0]
	)

    new_state = {
        'A': {'slave': [a_out], 'master': [a_master]},
        'B': {'slave': [b_out], 'master': [b_master]},
    }
    return (a_out, b_out), new_state


def same(a: TRANSISTOR_OUTPUT, b: TRANSISTOR_OUTPUT) -> bool:
    # Inputs may be 0/1 ints or POWER/GROUND; compare as signals
    return bool(a) == bool(b)


def register_file_cycle(state, write_data, write_addr, addr_a, addr_b, write_enable, n_bits=4):
    '''One clock cycle of register_file_4xN with int inputs.'''
    def step(clk, st):
        a, b, slave, master = register_file_4xN(
            int_to_bits(write_data, n_bits), int_to_bits(write_addr, 2),
            int_to_bits(addr_a, 2), int_to_bits(addr_b, 2),
            POWER if write_enable else GROUND, clk, st['slave'], st['master']
        )
        return (bits_to_int(a), bits_to_int(b)), {'slave': slave, 'master': master}

    return clock_cycle(step, state)


# ------------------------------ 5_instruction_set_architecture.ipynb

OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_NOT, OP_ROR, OP_CMP = range(0b0000, 0b1000)


OP_LDI, OP_LD, OP_ST, OP_JMP, OP_JZ, OP_JNZ, OP_JC, OP_HALT = range(0b1000, 0b10000)


def encode(opcode: int, rd: int = 0, ra: int = 0, rb: int = 0, imm: int = 0) -> list[TRANSISTOR_OUTPUT]:
    '''
    Build a 16-bit instruction (MSB-first bit list) from its fields.

    Example:
        - encode(OP_ADD, rd=1, ra=2, rb=3)
        - word = 0000 01 10 11 00 0000 = 0x06C0
    '''
    assert 0 <= opcode < 16 and 0 <= rd < 4 and 0 <= ra < 4 and 0 <= rb < 4 and 0 <= imm < 16
    word = (opcode << 12) | (rd << 10) | (ra << 8) | (rb << 6) | imm
    return int_to_bits(word, 16)


ZERO_4 = [GROUND, GROUND, GROUND, GROUND]


ONE_4 = [GROUND, GROUND, GROUND, POWER]


def next_pc_logic(
    pc: list[TRANSISTOR_OUTPUT],
    jump_target: list[TRANSISTOR_OUTPUT],
    take_jump: TRANSISTOR_OUTPUT,
    halt: TRANSISTOR_OUTPUT,
    reset: TRANSISTOR_OUTPUT
) -> list[TRANSISTOR_OUTPUT]:
    '''
    Choose the PC for the next cycle. Priority: reset > halt > jump > PC + 1.

    Inputs:
        - pc: current 4-bit PC
        - jump_target: 4-bit address to jump to (the instruction's imm field)
        - take_jump: 1 if a jump is taken this cycle
        - halt: 1 if the instruction is HALT
        - reset: 1 to restart from address 0
    '''
    pc_plus_one, _ = adder_subtractor_4bit(pc, ONE_4, is_subtraction=GROUND)

    next_pc = n_bit_mux_2to1(pc_plus_one, jump_target, take_jump)
    next_pc = n_bit_mux_2to1(next_pc, pc, halt)
    return n_bit_mux_2to1(next_pc, ZERO_4, reset)


def decode_instruction(instruction: list[TRANSISTOR_OUTPUT]) -> dict:
    '''
    Control Unit: split a 16-bit instruction into its fields, and decode the opcode into control signals.

    Returns a dict of:
        - fields: rd, ra, rb (2 bits each), imm (4 bits), alu_op (3 bits)
        - control signals: one wire each
    '''
    # Step 1: Split the fields (wiring only)
    op3, op2, op1, op0 = instruction[0:4]
    rd, ra, rb = instruction[4:6], instruction[6:8], instruction[8:10]
    imm = instruction[12:16]

    # Step 2: Decode the opcode
    is_alu = cmos_NOT(op3)
    group_lines = decoder_3to8(op2, op1, op0)
    is_ldi, is_ld, is_st, is_jmp, is_jz, is_jnz, is_jc, is_halt = [cmos_AND(op3, line) for line in group_lines]

    return {
        'rd': rd, 'ra': ra, 'rb': rb, 'imm': imm,
        'alu_op': (op2, op1, op0),
        'reg_write': cmos_OR(is_alu, cmos_OR(is_ldi, is_ld)),
        'ram_write': is_st,
        'flags_write': is_alu,
        'wb_from_imm': is_ldi,
        'wb_from_ram': is_ld,
        'is_jmp': is_jmp,
        'is_jz': is_jz,
        'is_jnz': is_jnz,
        'is_jc': is_jc,
        'is_halt': is_halt,
    }


def branch_logic(control: dict, flags: list[TRANSISTOR_OUTPUT]) -> TRANSISTOR_OUTPUT:
    '''
    Decide whether this instruction jumps.

    Inputs:
        - control: control signals from decode_instruction
        - flags: stored flags [ZERO, SIGN, CARRY, OVERFLOW] from the flags register
    '''
    zero, _, carry, _ = flags

    jz_taken = cmos_AND(control['is_jz'], zero)
    jnz_taken = cmos_AND(control['is_jnz'], cmos_NOT(zero))
    jc_taken = cmos_AND(control['is_jc'], carry)

    return cmos_OR(cmos_OR(control['is_jmp'], jz_taken), cmos_OR(jnz_taken, jc_taken))


def cpu_power_on_state() -> dict:
    '''
    All CPU state, with every latch at 0: PC, register file, flags register and RAM.
    The ROM isn't here because it's wiring, not state.
    '''
    return {
        'pc': power_on_state(1, 4),
        'regs': power_on_state(4, 4),
        'flags': power_on_state(1, 4),
        'ram': power_on_state(16, 4),
    }


def cpu_step(clk, state, rom_contents, reset=GROUND):
    '''
    One clock half of the CPU. Used as the step function for clock_cycle.

    Inputs:
        - clk: clock value for this half
        - state: CPU state (see cpu_power_on_state)
        - rom_contents: the program, up to 16 instructions of 16 bits each
        - reset: 1 to restart from address 0

    Returns:
        - (outputs, new_state). outputs holds the PC and instruction of this cycle, and whether it is HALT
    '''
    pc = state['pc']['slave'][0]
    flags = state['flags']['slave'][0]
    not_reset = cmos_NOT(reset)

    # 1. Fetch
    instruction = rom_16xN(rom_contents, pc)

    # 2. Decode
    control = decode_instruction(instruction)

    # 3. Read registers
    reg_a = read_port_4xN(state['regs']['slave'], control['ra'])
    reg_b = read_port_4xN(state['regs']['slave'], control['rb'])

    # 4. Execute. The RAM outputs the word at imm, and stores A on the rising edge for ST
    alu_result, alu_flags = alu_4bit(reg_a, reg_b, control['alu_op'])

    ram_data, ram_slave, ram_master = ram_16xN(
        write_data=reg_a,
        addr=control['imm'],
        write_enable=cmos_AND(control['ram_write'], not_reset),
        enable=clk,
        slave_state_matrix=state['ram']['slave'],
        master_state_matrix=state['ram']['master']
    )

    # 5. Write-back: the ALU result, or imm for LDI, or the RAM word for LD
    write_back = n_bit_mux_2to1(alu_result, control['imm'], control['wb_from_imm'])
    write_back = n_bit_mux_2to1(write_back, ram_data, control['wb_from_ram'])

    _, _, regs_slave, regs_master = register_file_4xN(
        write_data=write_back,
        write_addr=control['rd'],
        read_addr_a=control['ra'],
        read_addr_b=control['rb'],
        write_enable=cmos_AND(control['reg_write'], not_reset),
        enable=clk,
        slave_state_matrix=state['regs']['slave'],
        master_state_matrix=state['regs']['master']
    )

    new_flags = [alu_flags['ZERO'], alu_flags['SIGN'], alu_flags['CARRY'], alu_flags['OVERFLOW']]
    flags_slave, _, flags_master = n_bit_register(
        inputs=new_flags,
        enable=clk,
        load=cmos_AND(control['flags_write'], not_reset),
        slave_vals_prev=flags,
        master_vals_prev=state['flags']['master'][0]
    )

    # 6. Next PC
    take_jump = branch_logic(control, flags)
    next_pc = next_pc_logic(pc, control['imm'], take_jump, control['is_halt'], reset)

    pc_slave, _, pc_master = n_bit_register(
        inputs=next_pc,
        enable=clk,
        load=POWER,
        slave_vals_prev=pc,
        master_vals_prev=state['pc']['master'][0]
    )

    outputs = {
        'pc': pc,
        'instruction': instruction,
        'halted': cmos_AND(control['is_halt'], not_reset),
    }
    new_state = {
        'pc': {'slave': [pc_slave], 'master': [pc_master]},
        'regs': {'slave': regs_slave, 'master': regs_master},
        'flags': {'slave': [flags_slave], 'master': [flags_master]},
        'ram': {'slave': ram_slave, 'master': ram_master},
    }
    return outputs, new_state


def read_cpu(state: dict) -> dict:
    '''
    Stored CPU values as Python ints, for printing and testing. Not part of the circuit.
    '''
    return {
        'pc': bits_to_int(state['pc']['slave'][0]),
        'regs': [bits_to_int(word) for word in state['regs']['slave']],
        'flags': {name: 1 if bit else 0 for name, bit in zip(['ZERO', 'SIGN', 'CARRY', 'OVERFLOW'], state['flags']['slave'][0])},
        'ram': [bits_to_int(word) for word in state['ram']['slave']],
    }


def run_cpu(rom_contents: list[list[TRANSISTOR_OUTPUT]], max_cycles: int = 100, trace: bool = False):
    '''
    Power on, reset, then run the program until HALT.

    Returns:
        - (state, cycles): final CPU state, and the number of cycles run, counting the HALT cycle
          but not the reset cycle
    Raises:
        - RuntimeError if the program hasn't halted after max_cycles
    '''
    state = cpu_power_on_state()
    _, state = clock_cycle(lambda clk, st: cpu_step(clk, st, rom_contents, reset=POWER), state)

    for cycle in range(1, max_cycles + 1):
        outputs, state = clock_cycle(lambda clk, st: cpu_step(clk, st, rom_contents), state)

        if trace:
            print(f"cycle {cycle:3d}   pc = {bits_to_int(outputs['pc']):2d}   "
                  f"instruction = 0x{bits_to_int(outputs['instruction']):04X}   "
                  f"regs = {read_cpu(state)['regs']}")

        if outputs['halted']:
            return state, cycle

    raise RuntimeError(f'program did not halt within {max_cycles} cycles')


def print_cpu_state(state: dict):
    cpu = read_cpu(state)
    print(f"PC    : {cpu['pc']}")
    print('regs  : ' + '   '.join(f'R{i} = {v:2d}' for i, v in enumerate(cpu['regs'])))
    print('flags : ' + '   '.join(f'{name} = {v}' for name, v in cpu['flags'].items()))
    print('RAM   :')
    for row in range(4):
        print('        ' + '   '.join(f'[{4 * row + col:2d}] = {cpu["ram"][4 * row + col]:2d}' for col in range(4)))


def multiply_program(a: int, b: int) -> list[list[TRANSISTOR_OUTPUT]]:
    return [
        encode(OP_LDI, rd=1, imm=a),
        encode(OP_LDI, rd=2, imm=b),
        encode(OP_LDI, rd=3, imm=1),
        encode(OP_LDI, rd=0, imm=0),
        encode(OP_ADD, rd=0, ra=0, rb=1),   # 4: loop start
        encode(OP_SUB, rd=2, ra=2, rb=3),
        encode(OP_JNZ, imm=4),
        encode(OP_ST, ra=0, imm=0),
        encode(OP_HALT),
    ]


def alu_reference(opcode: int, a: int, b: int) -> int:
    '''
    Plain Python result of an ALU instruction on 4-bit unsigned a and b.
    '''
    rotate = b & 3
    return [
        (a + b) % 16,
        (a - b) % 16,
        a & b,
        a | b,
        a ^ b,
        ~a & 0xF,
        ((a >> rotate) | (a << (4 - rotate))) & 0xF,
        (int(a > b) << 1) | int(a == b),
    ][opcode]


def jump_program(jump_opcode: int, x: int, y: int) -> list[list[TRANSISTOR_OUTPUT]]:
    '''Sets flags with SUB x - y, then jumps over an instruction that writes R0 = 1.'''
    return [
        encode(OP_LDI, rd=1, imm=x),
        encode(OP_LDI, rd=2, imm=y),
        encode(OP_SUB, rd=3, ra=1, rb=2),
        encode(jump_opcode, imm=5),
        encode(OP_LDI, rd=0, imm=1),        # only runs if the jump is not taken
        encode(OP_HALT),                    # 5
    ]


# ------------------------------ 6_assembly_and_assembler.ipynb

INSTRUCTION_SET = {
    'ADD':  (OP_ADD << 12, 0xF000, ('rd', 'ra', 'rb')),
    'SUB':  (OP_SUB << 12, 0xF000, ('rd', 'ra', 'rb')),
    'AND':  (OP_AND << 12, 0xF000, ('rd', 'ra', 'rb')),
    'OR':   (OP_OR << 12, 0xF000, ('rd', 'ra', 'rb')),
    'XOR':  (OP_XOR << 12, 0xF000, ('rd', 'ra', 'rb')),
    'NOT':  (OP_NOT << 12, 0xF000, ('rd', 'ra')),
    'ROR':  (OP_ROR << 12, 0xF000, ('rd', 'ra', 'rb')),
    'CMP':  (OP_CMP << 12, 0xF000, ('rd', 'ra', 'rb')),
    'LDI':  (OP_LDI << 12, 0xF000, ('rd', 'imm')),
    'LD':   (OP_LD << 12, 0xF000, ('rd', '[imm]')),
    'ST':   (OP_ST << 12, 0xF000, ('ra', '[imm]')),
    'JMP':  (OP_JMP << 12, 0xF000, ('imm',)),
    'JZ':   (OP_JZ << 12, 0xF000, ('imm',)),
    'JNZ':  (OP_JNZ << 12, 0xF000, ('imm',)),
    'JC':   (OP_JC << 12, 0xF000, ('imm',)),
    'HALT': (OP_HALT << 12, 0xF0F0, ()),
}


FIELD_SHIFT = {'rd': 10, 'ra': 8, 'rb': 6, 'imm': 0}


ROM_WORDS = 16


LABEL_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class AssemblyError(Exception):
    '''
    An error in assembly source. The message starts with the line number.
    '''
    def __init__(self, line_number: int, message: str):
        super().__init__(f'line {line_number}: {message}')
        self.line_number = line_number


def parse_register(text: str, line_number: int) -> int:
    match = re.fullmatch(r'[Rr]([0-3])', text)
    if not match:
        raise AssemblyError(line_number, f'expected a register R0-R3, got {text!r}')
    return int(match.group(1))


def parse_value(text: str, labels: dict[str, int], line_number: int) -> int:
    '''
    A number (decimal, 0x hex or 0b binary) or a label. Must fit in 4 bits.
    '''
    if LABEL_PATTERN.match(text):
        if text.lower() not in labels:
            raise AssemblyError(line_number, f'undefined label {text!r}')
        return labels[text.lower()]
    try:
        value = int(text, 0)
    except ValueError:
        raise AssemblyError(line_number, f'expected a number or label, got {text!r}')
    if not 0 <= value <= 15:
        raise AssemblyError(line_number, f'{text} does not fit in 4 bits (0 to 15)')
    return value


def parse_lines(source: str, instruction_set: dict) -> tuple[list[tuple[int, str, list[str]]], dict[str, int]]:
    '''
    Pass 1: split the source into instructions, and record the address of every label.

    Returns:
        - instructions: (line number, name, operand texts) for each instruction, in address order
        - labels: label name -> address
    '''
    instructions = []
    labels = {}

    for line_number, line in enumerate(source.splitlines(), start=1):
        text = line.split(';')[0].strip()

        # Labels: any number of "name:" at the start of the line
        while ':' in text:
            label, text = text.split(':', 1)
            label, text = label.strip(), text.strip()
            if not LABEL_PATTERN.match(label):
                raise AssemblyError(line_number, f'invalid label name {label!r}')
            if label.upper() in instruction_set or re.fullmatch(r'[Rr][0-3]', label):
                raise AssemblyError(line_number, f'label {label!r} is an instruction or register name')
            if label.lower() in labels:
                raise AssemblyError(line_number, f'label {label!r} is already defined')
            labels[label.lower()] = len(instructions)

        if not text:
            continue

        name, _, rest = text.replace('\t', ' ').partition(' ')
        name = name.upper()
        if name not in instruction_set:
            raise AssemblyError(line_number, f'unknown instruction {name!r}')
        operands = [op.strip() for op in rest.split(',')] if rest.strip() else []
        instructions.append((line_number, name, operands))

    return instructions, labels


def encode_line(line_number: int, name: str, operands: list[str], labels: dict[str, int], instruction_set: dict) -> int:
    '''
    Pass 2: encode one instruction into a 16-bit word.
    '''
    base, _, formats = instruction_set[name]
    if len(operands) != len(formats):
        expected = ', '.join(formats) if formats else 'no operands'
        raise AssemblyError(line_number, f'{name} takes {len(formats)} operand(s) ({expected}), got {len(operands)}')

    word = base
    for text, fmt in zip(operands, formats):
        if fmt == '[imm]':
            if not (text.startswith('[') and text.endswith(']')):
                raise AssemblyError(line_number, f'{name} expects a RAM address in square brackets, got {text!r}')
            word |= parse_value(text[1:-1].strip(), labels, line_number) << FIELD_SHIFT['imm']
        elif fmt == 'imm':
            if text.startswith('['):
                raise AssemblyError(line_number, f'{name} expects a value, not a RAM address: {text!r}')
            word |= parse_value(text, labels, line_number) << FIELD_SHIFT['imm']
        else:
            word |= parse_register(text, line_number) << FIELD_SHIFT[fmt]
    return word


def assemble(source: str, instruction_set: dict = INSTRUCTION_SET) -> list[int]:
    '''
    Assemble source text into a list of 16-bit instruction words.

    Raises:
        - AssemblyError, with the line number, for any problem in the source
    '''
    instructions, labels = parse_lines(source, instruction_set)
    if len(instructions) > ROM_WORDS:
        raise AssemblyError(instructions[ROM_WORDS][0], f'program has {len(instructions)} instructions, but ROM holds {ROM_WORDS}')
    return [encode_line(line_number, name, operands, labels, instruction_set) for line_number, name, operands in instructions]


def words_to_rom(words: list[int]) -> list[list[TRANSISTOR_OUTPUT]]:
    '''
    16-bit words -> MSB-first bit lists, the format rom_16xN takes.
    '''
    return [int_to_bits(word, 16) for word in words]


MULTIPLY_SOURCE = '''
; R0 = R1 x R2, by adding R1 to R0, R2 times
    LDI R1, 3           ; a
    LDI R2, 5           ; b, counts down to 0
    LDI R3, 1           ; constant 1
    LDI R0, 0           ; total
loop:
    ADD R0, R0, R1      ; total = total + a
    SUB R2, R2, R3      ; b = b - 1, sets ZERO when b reaches 0
    JNZ loop
    ST R0, [0]          ; RAM[0] = total
    HALT
'''


def disassemble_word(word: int, instruction_set: dict = INSTRUCTION_SET) -> str:
    '''
    One 16-bit word -> assembly text.
    '''
    for name, (base, mask, formats) in instruction_set.items():
        if word & mask != base:
            continue
        operands = []
        for fmt in formats:
            if fmt in ('imm', '[imm]'):
                value = str(word & 0xF)
                operands.append(f'[{value}]' if fmt == '[imm]' else value)
            else:
                operands.append(f'R{(word >> FIELD_SHIFT[fmt]) & 3}')
        return f'{name} {", ".join(operands)}'.strip()
    return f'.word 0x{word:04X}'


def disassemble(words: list[int], instruction_set: dict = INSTRUCTION_SET) -> str:
    '''
    A program -> assembly text, one line per instruction, with its address as a comment.
    '''
    return '\n'.join(f'{disassemble_word(word, instruction_set):18s} ; {address}' for address, word in enumerate(words))


# ------------------------------ 7_software_execution.ipynb

OUTPUT_ADDRESS = 15


def format_trace_line(cycle: int, pc: int, word: int, cpu: dict, printed, instruction_set: dict) -> str:
    regs = ' '.join(f'R{i}={v:2d}' for i, v in enumerate(cpu['regs']))
    flags = ''.join(name[0] if cpu['flags'][name] else '.' for name in ['ZERO', 'SIGN', 'CARRY', 'OVERFLOW'])
    extra = f'   sp={cpu["sp"]:2d}' if 'sp' in cpu else ''
    out = f'   out: {printed}' if printed is not None else ''
    return f'{cycle:4d}  pc={pc:2d}  {disassemble_word(word, instruction_set):16s}  {regs}  flags={flags}{extra}{out}'


def run_with_output(
    rom_contents: list[list[TRANSISTOR_OUTPUT]],
    max_cycles: int = 200,
    trace: bool = False,
    step=cpu_step,
    power_on=cpu_power_on_state,
    read=read_cpu,
    instruction_set: dict = INSTRUCTION_SET
):
    '''
    Power on, reset, then run the program until HALT, collecting every value stored to OUTPUT_ADDRESS.

    Inputs:
        - rom_contents: the program, as bit lists (see words_to_rom)
        - trace: print one line per cycle: PC, instruction, registers, flags (Z S C V, '.' = 0), output
        - step, power_on, read: the CPU to run. Default: notebook 5's CPU

    Returns:
        - (state, cycles, output): final state, cycles run including HALT, and the printed values in order
    '''
    state = power_on()
    _, state = clock_cycle(lambda clk, st: step(clk, st, rom_contents, reset=POWER), state)
    output = []

    for cycle in range(1, max_cycles + 1):
        outputs, state = clock_cycle(lambda clk, st: step(clk, st, rom_contents), state)
        cpu = read(state)

        # ST to the output port: the RAM write the CPU's own decoder sees, at address OUTPUT_ADDRESS
        control = decode_instruction(outputs['instruction'])
        printed = None
        if control['ram_write'] and bits_to_int(control['imm']) == OUTPUT_ADDRESS:
            printed = cpu['ram'][OUTPUT_ADDRESS]
            output.append(printed)

        if trace:
            print(format_trace_line(cycle, bits_to_int(outputs['pc']), bits_to_int(outputs['instruction']), cpu, printed, instruction_set))

        if outputs['halted']:
            return state, cycle, output

    raise RuntimeError(f'program did not halt within {max_cycles} cycles')


def run_source(source: str, max_cycles: int = 200, trace: bool = False) -> list[int]:
    '''
    Assemble and run a program on notebook 5's CPU. Returns the printed values.
    '''
    _, _, output = run_with_output(words_to_rom(assemble(source)), max_cycles=max_cycles, trace=trace)
    return output


FIBONACCI_SOURCE = '''
; Print Fibonacci numbers until the next one doesn't fit in 4 bits
    LDI R0, 0           ; a
    LDI R1, 1           ; b
loop:
    ST R1, [15]         ; print b
    ADD R2, R0, R1      ; c = a + b
    JC done             ; c doesn't fit in 4 bits: stop
    OR R0, R1, R1       ; a = b
    OR R1, R2, R2       ; b = c
    JMP loop
done:
    HALT
'''


def reference_power_on() -> dict:
    return {
        'pc': 0,
        'regs': [0, 0, 0, 0],
        'flags': {'ZERO': 0, 'SIGN': 0, 'CARRY': 0, 'OVERFLOW': 0},
        'ram': [0] * 16,
    }


def to_signed(value: int) -> int:
    '''4-bit two's complement: 8 to 15 stand for -8 to -1.'''
    return value - 16 if value >= 8 else value


def reference_alu(opcode: int, a: int, b: int) -> tuple[int, dict]:
    result = alu_reference(opcode, a, b)
    if opcode == OP_ADD:
        carry, overflow = int(a + b > 15), int(not -8 <= to_signed(a) + to_signed(b) <= 7)
    elif opcode == OP_SUB:
        carry, overflow = int(a >= b), int(not -8 <= to_signed(a) - to_signed(b) <= 7)
    else:
        carry, overflow = 0, 0
    return result, {'ZERO': int(result == 0), 'SIGN': result >> 3, 'CARRY': carry, 'OVERFLOW': overflow}


def reference_step(cpu: dict, rom_words: list[int]) -> tuple[dict, bool]:
    '''
    Execute one instruction in plain Python.

    Returns:
        - (new_cpu, halted): the state after the instruction, and whether it was HALT
    '''
    cpu = copy.deepcopy(cpu)
    word = rom_words[cpu['pc']] if cpu['pc'] < len(rom_words) else 0
    opcode, rd, ra, rb, imm = word >> 12, (word >> 10) & 3, (word >> 8) & 3, (word >> 6) & 3, word & 0xF
    a, b = cpu['regs'][ra], cpu['regs'][rb]
    flags = cpu['flags']

    next_pc = (cpu['pc'] + 1) % 16
    halted = False

    if opcode < 8:
        cpu['regs'][rd], cpu['flags'] = reference_alu(opcode, a, b)
    elif opcode == OP_LDI:
        cpu['regs'][rd] = imm
    elif opcode == OP_LD:
        cpu['regs'][rd] = cpu['ram'][imm]
    elif opcode == OP_ST:
        cpu['ram'][imm] = a
    elif opcode == OP_JMP:
        next_pc = imm
    elif opcode == OP_JZ and flags['ZERO']:
        next_pc = imm
    elif opcode == OP_JNZ and not flags['ZERO']:
        next_pc = imm
    elif opcode == OP_JC and flags['CARRY']:
        next_pc = imm
    elif opcode == OP_HALT:
        next_pc, halted = cpu['pc'], True

    cpu['pc'] = next_pc
    return cpu, halted


def describe_mismatch(cycle: int, hardware: dict, reference: dict) -> str:
    lines = [f'cycle {cycle}: hardware and reference differ']
    for key in reference:
        if hardware.get(key) != reference[key]:
            lines.append(f'    {key}: hardware {hardware.get(key)}, reference {reference[key]}')
    return '\n'.join(lines)


def run_in_lockstep(
    rom_words: list[int],
    max_cycles: int = 100,
    step=cpu_step,
    power_on=cpu_power_on_state,
    read=read_cpu,
    reference=reference_step,
    reference_start=reference_power_on
) -> int:
    '''
    Run a program on the gate-level CPU and the reference simulator together, comparing after every instruction.

    Returns:
        - the number of cycles run (up to and including HALT, or max_cycles)
    Raises:
        - AssertionError at the first cycle where the two differ
    '''
    rom_contents = words_to_rom(rom_words)
    state = power_on()
    _, state = clock_cycle(lambda clk, st: step(clk, st, rom_contents, reset=POWER), state)
    expected = reference_start()

    for cycle in range(1, max_cycles + 1):
        outputs, state = clock_cycle(lambda clk, st: step(clk, st, rom_contents), state)
        expected, expected_halted = reference(expected, rom_words)

        actual = read(state)
        if actual != expected:
            raise AssertionError(describe_mismatch(cycle, actual, expected))
        if bool(outputs['halted']) != expected_halted:
            raise AssertionError(f'cycle {cycle}: hardware halted = {bool(outputs["halted"])}, reference halted = {expected_halted}')
        if expected_halted:
            return cycle

    return max_cycles


def buggy_reference(cpu, rom_words):
    word = rom_words[cpu['pc']] if cpu['pc'] < len(rom_words) else 0
    if word >> 12 == OP_JNZ:
        cpu = copy.deepcopy(cpu)
        cpu['pc'] = word & 0xF if cpu['flags']['ZERO'] else (cpu['pc'] + 1) % 16
        return cpu, False
    return reference_step(cpu, rom_words)


# ------------------------------ 8_stack_and_subroutines.ipynb

SUB_HALT, SUB_PUSH, SUB_POP, SUB_CALL, SUB_RET = range(5)


STACK_INSTRUCTION_SET = {
    **INSTRUCTION_SET,
    'PUSH': ((OP_HALT << 12) | (SUB_PUSH << 4), 0xF0F0, ('ra',)),
    'POP':  ((OP_HALT << 12) | (SUB_POP << 4), 0xF0F0, ('rd',)),
    'CALL': ((OP_HALT << 12) | (SUB_CALL << 4), 0xF0F0, ('imm',)),
    'RET':  ((OP_HALT << 12) | (SUB_RET << 4), 0xF0F0, ()),
}


def decode_instruction_with_stack(instruction: list[TRANSISTOR_OUTPUT]) -> dict:
    '''
    Notebook 5's control unit, plus the stack instructions under opcode 1111.
    '''
    control = decode_instruction(instruction)

    # Notebook 5 decodes every 1111 opcode as HALT. Here the sub-opcode in bits 7-4 decides
    is_opcode_1111 = control['is_halt']
    sub_lines = decoder_4to16(*instruction[8:12])
    is_halt, is_push, is_pop, is_call, is_ret = [cmos_AND(is_opcode_1111, line) for line in sub_lines[:5]]

    push_or_call = cmos_OR(is_push, is_call)
    pop_or_ret = cmos_OR(is_pop, is_ret)

    control.update({
        'is_halt': is_halt,
        'is_push': is_push,
        'is_pop': is_pop,
        'is_call': is_call,
        'is_ret': is_ret,
        'push_or_call': push_or_call,
        'pop_or_ret': pop_or_ret,
        'reg_write': cmos_OR(control['reg_write'], is_pop),
        'wb_from_ram': cmos_OR(control['wb_from_ram'], is_pop),
        'ram_write': cmos_OR(control['ram_write'], push_or_call),
        'sp_write': cmos_OR(push_or_call, pop_or_ret),
    })
    return control


def cpu_with_stack_power_on_state() -> dict:
    state = cpu_power_on_state()
    state['sp'] = power_on_state(1, 4)
    return state


def cpu_step_with_stack(clk, state, rom_contents, reset=GROUND):
    '''
    One clock half of the CPU with a stack. Same steps as notebook 5's cpu_step, plus the stack.
    '''
    pc = state['pc']['slave'][0]
    sp = state['sp']['slave'][0]
    flags = state['flags']['slave'][0]
    not_reset = cmos_NOT(reset)

    # 1. Fetch
    instruction = rom_16xN(rom_contents, pc)

    # 2. Decode
    control = decode_instruction_with_stack(instruction)

    # 3. Read registers
    reg_a = read_port_4xN(state['regs']['slave'], control['ra'])
    reg_b = read_port_4xN(state['regs']['slave'], control['rb'])

    # 4. Execute
    alu_result, alu_flags = alu_4bit(reg_a, reg_b, control['alu_op'])
    pc_plus_one, _ = adder_subtractor_4bit(pc, ONE_4, is_subtraction=GROUND)
    sp_minus_one, _ = adder_subtractor_4bit(sp, ONE_4, is_subtraction=POWER)
    sp_plus_one, _ = adder_subtractor_4bit(sp, ONE_4, is_subtraction=GROUND)

    # RAM address: imm (LD, ST), SP - 1 (PUSH, CALL) or SP (POP, RET)
    ram_addr = n_bit_mux_2to1(control['imm'], sp_minus_one, control['push_or_call'])
    ram_addr = n_bit_mux_2to1(ram_addr, sp, control['pop_or_ret'])

    # RAM write data: register A (ST, PUSH) or the return address (CALL)
    ram_write_data = n_bit_mux_2to1(reg_a, pc_plus_one, control['is_call'])

    ram_data, ram_slave, ram_master = ram_16xN(
        write_data=ram_write_data,
        addr=ram_addr,
        write_enable=cmos_AND(control['ram_write'], not_reset),
        enable=clk,
        slave_state_matrix=state['ram']['slave'],
        master_state_matrix=state['ram']['master']
    )

    # 5. Write-back: the ALU result, or imm for LDI, or the RAM word for LD and POP
    write_back = n_bit_mux_2to1(alu_result, control['imm'], control['wb_from_imm'])
    write_back = n_bit_mux_2to1(write_back, ram_data, control['wb_from_ram'])

    _, _, regs_slave, regs_master = register_file_4xN(
        write_data=write_back,
        write_addr=control['rd'],
        read_addr_a=control['ra'],
        read_addr_b=control['rb'],
        write_enable=cmos_AND(control['reg_write'], not_reset),
        enable=clk,
        slave_state_matrix=state['regs']['slave'],
        master_state_matrix=state['regs']['master']
    )

    new_flags = [alu_flags['ZERO'], alu_flags['SIGN'], alu_flags['CARRY'], alu_flags['OVERFLOW']]
    flags_slave, _, flags_master = n_bit_register(
        inputs=new_flags,
        enable=clk,
        load=cmos_AND(control['flags_write'], not_reset),
        slave_vals_prev=flags,
        master_vals_prev=state['flags']['master'][0]
    )

    # SP: down for PUSH and CALL, up for POP and RET. Reset empties the stack (SP = 0)
    next_sp = n_bit_mux_2to1(sp_minus_one, sp_plus_one, control['pop_or_ret'])
    next_sp = n_bit_mux_2to1(next_sp, ZERO_4, reset)
    sp_slave, _, sp_master = n_bit_register(
        inputs=next_sp,
        enable=clk,
        load=cmos_OR(cmos_AND(control['sp_write'], not_reset), reset),
        slave_vals_prev=sp,
        master_vals_prev=state['sp']['master'][0]
    )

    # 6. Next PC: CALL jumps to imm, RET jumps to the return address read from the stack
    take_jump = cmos_OR(branch_logic(control, flags), cmos_OR(control['is_call'], control['is_ret']))
    jump_target = n_bit_mux_2to1(control['imm'], ram_data, control['is_ret'])
    next_pc = next_pc_logic(pc, jump_target, take_jump, control['is_halt'], reset)

    pc_slave, _, pc_master = n_bit_register(
        inputs=next_pc,
        enable=clk,
        load=POWER,
        slave_vals_prev=pc,
        master_vals_prev=state['pc']['master'][0]
    )

    outputs = {
        'pc': pc,
        'instruction': instruction,
        'halted': cmos_AND(control['is_halt'], not_reset),
    }
    new_state = {
        'pc': {'slave': [pc_slave], 'master': [pc_master]},
        'sp': {'slave': [sp_slave], 'master': [sp_master]},
        'regs': {'slave': regs_slave, 'master': regs_master},
        'flags': {'slave': [flags_slave], 'master': [flags_master]},
        'ram': {'slave': ram_slave, 'master': ram_master},
    }
    return outputs, new_state


def read_cpu_with_stack(state: dict) -> dict:
    cpu = read_cpu(state)
    cpu['sp'] = bits_to_int(state['sp']['slave'][0])
    return cpu


def run_source_with_stack(source: str, max_cycles: int = 200, trace: bool = False):
    '''
    Assemble with the stack instructions and run on the CPU with a stack.
    Returns (state as ints, cycles, printed values).
    '''
    state, cycles, output = run_with_output(
        words_to_rom(assemble(source, STACK_INSTRUCTION_SET)),
        max_cycles=max_cycles,
        trace=trace,
        step=cpu_step_with_stack,
        power_on=cpu_with_stack_power_on_state,
        read=read_cpu_with_stack,
        instruction_set=STACK_INSTRUCTION_SET
    )
    return read_cpu_with_stack(state), cycles, output


PUSH_POP_SOURCE = '''
    LDI R0, 1
    LDI R1, 2
    LDI R2, 3
    PUSH R0             ; stack: 1
    PUSH R1             ; stack: 1 2
    PUSH R2             ; stack: 1 2 3
    POP R3              ; R3 = 3, stack: 1 2
    POP R0              ; R0 = 2, stack: 1
    POP R1              ; R1 = 1, stack empty
    HALT
'''


RECURSIVE_SUM_SOURCE = '''
; Print sum(5) = 5 + 4 + 3 + 2 + 1, computed recursively
    LDI R1, 5           ; argument n
    LDI R3, 1           ; constant 1, never changed
    CALL sum            ; R0 = sum(R1)
    ST R0, [15]         ; print the result
    HALT

; sum(n) = n + sum(n - 1), sum(0) = 0
; argument in R1 (kept), result in R0, uses R2
sum:
    LDI R0, 0           ; result for the base case
    OR R2, R1, R1       ; copy n, which sets ZERO if n == 0
    JZ sum_done         ; n == 0: return 0
    PUSH R1             ; save n
    SUB R1, R1, R3      ; n - 1
    CALL sum            ; R0 = sum(n - 1)
    POP R1              ; restore n
    ADD R0, R0, R1      ; R0 = n + sum(n - 1)
sum_done:
    RET
'''


def reference_power_on_with_stack() -> dict:
    cpu = reference_power_on()
    cpu['sp'] = 0
    return cpu


def reference_step_with_stack(cpu: dict, rom_words: list[int]) -> tuple[dict, bool]:
    '''
    Notebook 7's reference_step, plus the stack instructions under opcode 1111.
    '''
    word = rom_words[cpu['pc']] if cpu['pc'] < len(rom_words) else 0
    if word >> 12 != OP_HALT:
        new_cpu, halted = reference_step({k: v for k, v in cpu.items() if k != 'sp'}, rom_words)
        new_cpu['sp'] = cpu['sp']
        return new_cpu, halted

    cpu = copy.deepcopy(cpu)
    sub, rd, ra, imm = (word >> 4) & 0xF, (word >> 10) & 3, (word >> 8) & 3, word & 0xF
    pc, sp = cpu['pc'], cpu['sp']
    next_pc, halted = (pc + 1) % 16, False

    if sub == SUB_HALT:
        next_pc, halted = pc, True
    elif sub == SUB_PUSH:
        sp = (sp - 1) % 16
        cpu['ram'][sp] = cpu['regs'][ra]
    elif sub == SUB_POP:
        cpu['regs'][rd] = cpu['ram'][sp]
        sp = (sp + 1) % 16
    elif sub == SUB_CALL:
        sp = (sp - 1) % 16
        cpu['ram'][sp] = (pc + 1) % 16
        next_pc = imm
    elif sub == SUB_RET:
        next_pc = cpu['ram'][sp]
        sp = (sp + 1) % 16

    cpu['pc'], cpu['sp'] = next_pc, sp
    return cpu, halted


def run_in_lockstep_with_stack(rom_words: list[int], max_cycles: int = 100) -> int:
    return run_in_lockstep(
        rom_words,
        max_cycles=max_cycles,
        step=cpu_step_with_stack,
        power_on=cpu_with_stack_power_on_state,
        read=read_cpu_with_stack,
        reference=reference_step_with_stack,
        reference_start=reference_power_on_with_stack
    )


# ------------------------------ 9_compiler.ipynb

KEYWORDS = {'while', 'if', 'out'}


SYMBOLS = {'=', '+', '-', '&', '|', '^', '(', ')', '{', '}'}


class CompileError(Exception):
    '''
    An error in source code. The message starts with the line number.
    '''
    def __init__(self, line_number: int, message: str):
        super().__init__(f'line {line_number}: {message}')
        self.line_number = line_number


@dataclass
class Token:
    kind: str       # 'number', 'name', 'keyword', 'symbol' or 'end'
    text: str
    line: int


def tokenize(source: str) -> list[Token]:
    tokens = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        text = line.split('#')[0]
        for match in re.finditer(r'\s*(?:(\d+)|([A-Za-z_][A-Za-z0-9_]*)|(\S))', text):
            number, name, symbol = match.groups()
            if number:
                tokens.append(Token('number', number, line_number))
            elif name:
                tokens.append(Token('keyword' if name in KEYWORDS else 'name', name, line_number))
            elif symbol:
                if symbol not in SYMBOLS:
                    raise CompileError(line_number, f'unexpected character {symbol!r}')
                tokens.append(Token('symbol', symbol, line_number))
    last_line = tokens[-1].line if tokens else 1
    tokens.append(Token('end', '', last_line))
    return tokens


@dataclass
class Number:
    value: int


@dataclass
class Variable:
    name: str
    line: int


@dataclass
class Assign:
    target: Variable
    left: Number | Variable
    op: str | None
    right: Number | Variable | None


@dataclass
class Out:
    value: Number | Variable


@dataclass
class While:
    condition: Variable
    body: list


@dataclass
class If:
    condition: Variable
    body: list


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def peek(self) -> Token:
        return self.tokens[self.position]

    def take(self) -> Token:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def expect(self, text: str) -> Token:
        token = self.take()
        if token.text != text:
            found = repr(token.text) if token.kind != 'end' else 'the end of the program'
            raise CompileError(token.line, f'expected {text!r}, found {found}')
        return token

    def parse_program(self) -> list:
        statements = []
        while self.peek().kind != 'end':
            statements.append(self.parse_statement())
        return statements

    def parse_block(self) -> list:
        self.expect('{')
        statements = []
        while self.peek().text != '}':
            if self.peek().kind == 'end':
                raise CompileError(self.peek().line, "missing '}' at the end of a block")
            statements.append(self.parse_statement())
        self.expect('}')
        return statements

    def parse_statement(self):
        token = self.peek()
        if token.text == 'out':
            self.take()
            self.expect('(')
            value = self.parse_operand()
            self.expect(')')
            return Out(value)
        if token.text in ('while', 'if'):
            self.take()
            condition = self.parse_variable()
            body = self.parse_block()
            return While(condition, body) if token.text == 'while' else If(condition, body)
        if token.kind == 'name':
            target = self.parse_variable()
            self.expect('=')
            left = self.parse_operand()
            if self.peek().text in ('+', '-', '&', '|', '^'):
                op = self.take().text
                return Assign(target, left, op, self.parse_operand())
            return Assign(target, left, None, None)
        raise CompileError(token.line, f'expected a statement, found {token.text!r}')

    def parse_variable(self) -> Variable:
        token = self.take()
        if token.kind == 'keyword':
            raise CompileError(token.line, f'{token.text!r} is a keyword, not a variable name')
        if token.kind != 'name':
            raise CompileError(token.line, f'expected a variable name, found {token.text!r}')
        return Variable(token.text, token.line)

    def parse_operand(self) -> Number | Variable:
        token = self.peek()
        if token.kind == 'number':
            self.take()
            value = int(token.text)
            if value > 15:
                raise CompileError(token.line, f'{value} does not fit in 4 bits (0 to 15)')
            return Number(value)
        return self.parse_variable()


def parse(source: str) -> list:
    return Parser(tokenize(source)).parse_program()


VARIABLE_REGISTERS = ['R0', 'R1', 'R2']


SCRATCH_REGISTER = 'R3'


ASSEMBLY_OPERATORS = {'+': 'ADD', '-': 'SUB', '&': 'AND', '|': 'OR', '^': 'XOR'}


def apply_operator(op: str, a: int, b: int) -> int:
    '''An operator on 4-bit values, wrapping modulo 16 like the ALU.'''
    return {'+': a + b, '-': a - b, '&': a & b, '|': a | b, '^': a ^ b}[op] % 16


class CodeGenerator:
    def __init__(self):
        self.registers = {}         # variable name -> register
        self.lines = []
        self.label_count = 0

    def emit(self, line: str):
        self.lines.append(line)

    def new_labels(self, kind: str) -> tuple[str, str]:
        number = self.label_count
        self.label_count += 1
        return f'{kind}_{number}', f'end_{number}'

    def read_register(self, variable: Variable) -> str:
        if variable.name not in self.registers:
            raise CompileError(variable.line, f'variable {variable.name!r} is used before it is assigned')
        return self.registers[variable.name]

    def write_register(self, variable: Variable) -> str:
        if variable.name not in self.registers:
            if len(self.registers) == len(VARIABLE_REGISTERS):
                raise CompileError(variable.line, f'too many variables: at most {len(VARIABLE_REGISTERS)}, one per register')
            self.registers[variable.name] = VARIABLE_REGISTERS[len(self.registers)]
        return self.registers[variable.name]

    def operand_register(self, operand: Number | Variable) -> str:
        '''The register holding an operand. A number is loaded into the scratch register first.'''
        if isinstance(operand, Number):
            self.emit(f'    LDI {SCRATCH_REGISTER}, {operand.value}')
            return SCRATCH_REGISTER
        return self.read_register(operand)

    def statement(self, node):
        if isinstance(node, Assign):
            self.assign(node)
        elif isinstance(node, Out):
            self.emit(f'    ST {self.operand_register(node.value)}, [{OUTPUT_ADDRESS}]')
        elif isinstance(node, (While, If)):
            self.block(node)

    def assign(self, node: Assign):
        if node.op is None:
            if isinstance(node.left, Number):
                self.emit(f'    LDI {self.write_register(node.target)}, {node.left.value}')
            else:
                source = self.read_register(node.left)
                self.emit(f'    OR {self.write_register(node.target)}, {source}, {source}')
            return

        if isinstance(node.left, Number) and isinstance(node.right, Number):
            value = apply_operator(node.op, node.left.value, node.right.value)
            self.emit(f'    LDI {self.write_register(node.target)}, {value}')
            return

        # Operands are read before the target gets a register, so `x = x + 1` with x unassigned is an error
        left = self.operand_register(node.left)
        right = self.operand_register(node.right)
        self.emit(f'    {ASSEMBLY_OPERATORS[node.op]} {self.write_register(node.target)}, {left}, {right}')

    def block(self, node: While | If):
        start, end = self.new_labels('while' if isinstance(node, While) else 'if')
        condition = self.read_register(node.condition)
        self.emit(f'{start}:')
        self.emit(f'    OR {condition}, {condition}, {condition}')
        self.emit(f'    JZ {end}')
        for statement in node.body:
            self.statement(statement)
        if isinstance(node, While):
            self.emit(f'    JMP {start}')
        self.emit(f'{end}:')


def compile_program(source: str) -> str:
    '''
    Source code -> assembly text for notebook 6's assembler.
    '''
    generator = CodeGenerator()
    for statement in parse(source):
        generator.statement(statement)
    generator.emit('    HALT')
    return '\n'.join(generator.lines)


FIBONACCI_PROGRAM = '''
a = 0
b = 1
n = 7
while n {
    out(b)
    b = a + b       # next number
    a = b - a       # a = old b
    n = n - 1
}
'''


def compile_and_run(source: str, max_cycles: int = 500, trace: bool = False) -> list[int]:
    '''
    Compile, assemble and run a program on notebook 5's CPU. Returns the printed values.
    '''
    rom_contents = words_to_rom(assemble(compile_program(source)))
    _, _, output = run_with_output(rom_contents, max_cycles=max_cycles, trace=trace)
    return output


def interpret(source: str, max_steps: int = 10_000) -> list[int]:
    '''
    Run a program directly from its syntax tree, without compiling. Returns the printed values.
    '''
    variables = {}
    output = []
    steps = 0

    def value(operand):
        return operand.value if isinstance(operand, Number) else variables[operand.name]

    def run(statements):
        nonlocal steps
        for node in statements:
            steps += 1
            if steps > max_steps:
                raise RuntimeError('program did not finish')
            if isinstance(node, Assign):
                left = value(node.left)
                variables[node.target.name] = left if node.op is None else apply_operator(node.op, left, value(node.right))
            elif isinstance(node, Out):
                output.append(value(node.value))
            elif isinstance(node, While):
                while variables[node.condition.name]:
                    run(node.body)
            elif isinstance(node, If):
                if variables[node.condition.name]:
                    run(node.body)

    run(parse(source))
    return output


def expect_error(error_type, source: str, line_number: int, message: str):
    try:
        compile_program(source)
    except error_type as error:
        assert error.line_number == line_number, f'{source!r}: line {error.line_number}, want {line_number}'
        assert message in str(error), f'{source!r}: {str(error)!r} should mention {message!r}'
    else:
        raise AssertionError(f'{source!r} should not compile')


def random_program(rng: random.Random) -> str:
    names = ['a', 'b', 'c']
    lines = [f'{name} = {rng.randrange(16)}' for name in names]

    def operand():
        return rng.choice(names) if rng.random() < 0.7 else str(rng.randrange(16))

    for _ in range(rng.randrange(2, 6)):
        kind = rng.random()
        if kind < 0.5:
            op = rng.choice(['+', '-', '&', '|', '^'])
            lines.append(f'{rng.choice(names)} = {operand()} {op} {operand()}')
        elif kind < 0.8:
            lines.append(f'out({operand()})')
        else:
            lines.append(f'if {rng.choice(names)} {{ out({operand()}) }}')
    return '\n'.join(lines)

POWER = True
GROUND = None
type TRANSISTOR_OUTPUT = POWER | GROUND

def pmos(gate_signal: TRANSISTOR_OUTPUT, source: bool = POWER) -> TRANSISTOR_OUTPUT:
    """
    Pass through source signal when gate_signal is False (i.e. low power)
    None when gate_signal is True (i.e. high power)
    """
    return source if not gate_signal else None

def nmos(gate_signal: TRANSISTOR_OUTPUT, source: bool = POWER) -> POWER | GROUND:
    """
    Pass through source signal when gate_signal is True (i.e. high power)
    None when gate_signal is False (i.e low power)
    """
    return source if gate_signal else None

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
    ## - If (0, 0) --> 1
    ##    - PA returns 1, PB returns 1, PA2 returns 0, PB2 returns 0
    ##    - ✔ Power flows down left branch
    ##    - NA returns 0, NB2 returns 1, NA2 returns 1, NB returns 0
    ##    - ✘ Both drain branches are not connected 
    ##    - Output: POWER (1)
    ## - If (0, 1) --> 0
    ##    - PA returns 1, PB returns 0, PA2 returns 0, PB2 returns 1
    ##    - ✘ No powers to both paths 
    ##    - NA returns 0, NB2 returns 0, NA2 returns 1, NB returns 1
    ##    - ✔ Right drain branch connected
    ##    - Output: GROUND (0)
    ## - If (1, 0) --> 0
    ##    - PA returns 0, PB returns 1, PA2 returns 1, PB2 returns 0
    ##    - ✘ No powers to both paths 
    ##    - NA returns 1, NB2 returns 1, NA2 returns 0, NB returns 0
    ##    - ✔ Left drain branch connected
    ##    - Output: GROUND (0)
    ## - If (1, 1)
    ##    - PA returns 0, PB returns 0, PA2 returns 1, PB2 returns 1
    ##    - ✔ Power flows down right branch
    ##    - NA returns 1, NB2 returns 0, NA2 returns 0, NB returns 1
    ##    - ✘ Both drain branches are not connected 
    ##    - Output: POWER (1)

    input1_inv = cmos_NOT(input1)
    input2_inv = cmos_NOT(input2)

    pmos_A = pmos(input1, power)
    pmos_B = pmos(input2, pmos_A)

    pmos_A2 = pmos(input1_inv, power)
    pmos_B2 = pmos(input2_inv, pmos_A2)

    nmos_A = nmos(input1, power)
    nmos_B2 = nmos(input2_inv, nmos_A)

    nmos_A2 = nmos(input1_inv, power)
    nmos_B = nmos(input2, nmos_A2)

    if pmos_B is not None or pmos_B2 is not None:
        return power
    elif nmos_B is not None or nmos_B2 is not None:
        return GROUND
    else:
        return None  # Floating state (should not occur in valid CMOS design)

def cmos_XOR(input1: TRANSISTOR_OUTPUT, input2: TRANSISTOR_OUTPUT, ground: bool = GROUND) -> TRANSISTOR_OUTPUT:
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
    or_out = cmos_OR(input1, input2, ground=ground)
    nand_out = cmos_NAND(input1, input2, ground=ground)
    return cmos_AND(or_out, nand_out, ground=ground)
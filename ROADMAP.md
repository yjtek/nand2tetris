Roadmap: From Stateless Logic to Software Execution

4_stateless_to_stateful_ops.ipynb (Sequential Logic)

- SR Latch & D Latch: Build basic 1-bit memory cells using cross-coupled NOR/NAND gates to hold state.
- Flip-Flops: Combine latches to form edge-triggered D Flip-Flops that update only on clock transitions.
- Registers: Chain flip-flops in parallel to construct $N$-bit registers to store data words.
- RAM & Register File: Use decoders and MUXes from Notebook 3 to create an addressable memory grid (SRAM) and multi-register storage.
- Clock driver: Write a `tick()` that drives CLK 0 then 1 and carries every master/slave state forward. Right now each stateful function takes and returns its own state, and nothing owns it between calls.
- Two read ports: The ALU needs A and B in the same cycle. `register_file_4xN` has one read address.
- Read-during-write: Decide whether a read in the same tick as a write sees the old or new value. `register_file_4xN` currently returns the new one.
- Data RAM: A register file of 4 words is not enough to hold program variables. Build a larger RAM (e.g. 16 words, 4-bit address) the same way.
- ROM: Instruction memory that the program is loaded into. Read-only, so no flip-flops needed per bit. Decide how it is wired.
- Shared library: `utils.py` has `mux_2to1`, `mux_4to1`, `decoder_2to4` copied from Notebook 3. Notebook 5 also needs `n_bit_mux_2to1`, the adders, and `alu_4bit`. Copies drift from the notebook; consider making `utils.py` the only definition.
- Tests: Truth-table checks for every gate and block. Bugs compound upward, and a CPU bug is very hard to trace back to a gate.

5_instruction_set_architecture.ipynb (The CPU & ISA)

- Word width: Decide data width and instruction width before anything else. With a 4-bit word, one instruction cannot hold an opcode plus two register addresses plus a constant. Either widen the ALU (8-bit), or make instructions wider than data words.
- Memory layout: Decide whether instructions and data share one memory (von Neumann) or use separate ROM and RAM (Harvard). Harvard lets fetch and data access happen in the same cycle.
- Single-cycle vs multi-cycle: Decide whether each instruction takes one tick or several. Multi-cycle needs a small state machine (fetch, decode, execute) driven by its own state register.
- Clock & Program Counter (PC): Build a counter register that auto-increments to track current instruction memory addresses.
- PC control: PC needs three inputs beyond the clock: increment (adder with B=1), load (for jumps), and reset (start at address 0).
- Instruction Register (IR) & Decoder: Combine your 3-to-8 decoder logic with control logic to split instruction words into Opcode, Src Register, and Dest Register.
- Flags register: The ALU flags (Zero, Sign, Carry, Overflow) vanish after the cycle. Store them in a register so the next instruction can branch on them.
- Branch logic: Conditional jump (e.g. jump if Zero) loads the PC from the instruction instead of incrementing. Without this there are no loops, and no Fibonacci.
- Immediates: An instruction to put a constant into a register. Without it, the only way to get numbers in is to pre-fill RAM.
- Load / Store: Move words between the register file and data RAM.
- HALT: An instruction that stops the clock driver, so the simulation knows the program is done.
- The Control Unit (CU): Wire the ALU, RAM, and Register File together. Use opcodes to generate control signals that route data across the system bus.
- Fetch-Decode-Execute Cycle: Implement the hardware loop that retrieves instructions, decodes them, and executes them via the ALU.
- Output: Decide how you see results. Simplest is a memory dump after HALT. Next simplest is an output register mapped to a fixed address.

6_assembly_and_assembler.ipynb (Machine Code to Assembly)

- Instruction Set Definition: Design a simple machine language (e.g., 0001 = ADD, 0010 = LOAD)
- Assembler Implementation: Write a simple Python script to translate human-readable assembly instructions (e.g., ADD R1, R2) into raw binary strings/bytes.
- Labels: Allow `LOOP:` and `JZ LOOP`. Needs two passes: first pass records label addresses, second pass emits binary.
- Error reporting: Reject unknown opcodes, bad register names, and constants that do not fit in the immediate field. Silent truncation will show up later as a wrong answer.
- Disassembler: Binary back to assembly. Useful when tracing the CPU step by step.

7_software_execution.ipynb (Writing Software)

- Software Runtime: Write an application in your custom assembly language (e.g., calculating a Fibonacci sequence or a loop-based multiplier).
- Execution: Pass your assembled machine code into the simulated hardware top-level function and observe transistors, gates, registers, and memory update step by step.
- Trace output: Print PC, IR, registers, and flags each instruction. Gate-level output for every tick will be unreadable.
- Reference simulator: A plain-Python version of the ISA (no gates). Run the same program on both and compare state after every instruction. This is how you find hardware bugs.
- Overflow: With 4 or 8 bits, Fibonacci overflows fast. Decide what the program does when it does.

8_stack_and_subroutines.ipynb (Optional: Functions)

- Stack pointer: A register that points into RAM, with PUSH and POP.
- CALL / RET: CALL pushes the return address and jumps. RET pops it back into the PC.
- Calling convention: Decide which registers hold arguments and return values, and which ones a function must preserve.
- Recursion: A recursive program (e.g. factorial) to prove the stack works.

9_compiler.ipynb (Optional: High-Level Language to Assembly)

- Language: A tiny language with variables, `+ - & |`, `if`, `while`.
- Tokenizer: Source text to tokens.
- Parser: Tokens to a syntax tree.
- Code generation: Syntax tree to your assembly, using the stack for intermediate values.
- Variable allocation: Map each variable to a RAM address.
- End to end: Write Fibonacci in your language, compile, assemble, run on the gate-level CPU.

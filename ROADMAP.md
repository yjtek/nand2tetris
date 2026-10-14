Roadmap: From Stateless Logic to Software Execution

4_state_and_memory.ipynb (Sequential Logic)
- SR Latch & D Latch: Build basic 1-bit memory cells using cross-coupled NOR/NAND gates to hold state.
- Flip-Flops: Combine latches to form edge-triggered D Flip-Flops that update only on clock transitions.
- Registers: Chain flip-flops in parallel to construct $N$-bit registers to store data words.
- RAM & Register File: Use decoders and MUXes from Notebook 3 to create an addressable memory grid (SRAM) and multi-register storage.  

5_instruction_set_architecture.ipynb (The CPU & ISA)
- Clock & Program Counter (PC): Build a counter register that auto-increments to track current instruction memory addresses.
- Instruction Register (IR) & Decoder: Combine your 3-to-8 decoder logic with control logic to split instruction words into Opcode, Src Register, and Dest Register.  
- The Control Unit (CU): Wire the ALU, RAM, and Register File together. Use opcodes to generate control signals that route data across the system bus.  
- Fetch-Decode-Execute Cycle: Implement the hardware loop that retrieves instructions, decodes them, and executes them via the ALU.  

6_assembly_and_assembler.ipynb (Machine Code to Assembly)
- Instruction Set Definition: Design a simple machine language (e.g., 0001 = ADD, 0010 = LOAD)
- Assembler Implementation: Write a simple Python script to translate human-readable assembly instructions (e.g., ADD R1, R2) into raw binary strings/bytes.  

7_software_execution.ipynb (Writing Software)
- Software Runtime: Write an application in your custom assembly language (e.g., calculating a Fibonacci sequence or a loop-based multiplier).
- Execution: Pass your assembled machine code into the simulated hardware top-level function and observe transistors, gates, registers, and memory update step by step. 
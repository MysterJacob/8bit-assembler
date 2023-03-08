# 8bit-assembler
An assembler I made for my 8 bit computer

## Instrucion set
| ID | Opcode | VALUES | Hexcode | Description |
|---|---|---|---|---|
| 0	| NOP	| 0x00	0x00	| 0x00	| No instruction |
| 1	| HLT	| 0x06	0x00	| 0x01	| Halts the clock |
| 2	| MOV	| 0x81	0x00	| 0x02	| Sets ram adress to Z |
| 3	| ARL	| 0x15	0x00	| 0x03	| Loads from current Adress to A register |
| 4	| BRL	| 0x0D	0x00	| 0x04	| Loads from current Adress to B register
| 5	| LVA	| 0x11	0x00	| 0x05	| Loads [Z] value to A register
| 6	| LVB		| 0x09	0x00	| 0x06	| Loads [Z] value to B register
| 7	| ADD	| 0x12	0x00	| 	0x07	| Adds A register to B, stores in A
| 8	| SUB	| 0x0A	0x01	| 0x08	| Subs A register from B, stores in B
| 9	| STORA	| 0x64	0x00	| 0x09	| Stores value of A register in  current adress
| 10	| STORB	| 0x63	0x00	| 0x0A	| Stores value of B register in  current adress
| 11	| RLV	| 0x61	0x00	| 0x0B	| Stores value of argument in current adress
| 12	| OUTA	| 0x04	0x02	| 0x0C	| A Register -> Output Register
| 13	| OUTB	| 0x03	0x02	| 0x0D	| B Register -> Output Register
| 14	| JMP	| 0x01	0x20	| 0x0E	| Uncodnitional jump to [Z]
| 15	| CMP	| 0x02	0x41	| 0x0F	| Compares numbers in registers and sets flags
| 16	| OUTAL	| 0x02	0x02	| 0x10	| ALU -> Output Register
| 17	| OUTR	| 0x05	0x02	| 0x11	| Ram -> Output Register
| 18	| OUTV	| 0x01	0x02	| 0x12	| Rom argument to Output register
| 19	| STORR	| 0x84	0x00	| 0x13	| ALU -> Current Adress
| 20	| CMPA	| 0x04	0x40	| 0x14	| Compare numbers in register A with 0
| 21	| CMPB	| 0x03	0x40	| 0x15	| Compare numbers in register A with 0
| 22	| JOF	| 0x01	0x28	| 0x16	| Jump if overflow
| 23	| JPO	| 0x01	0x18	| 0x17	| Jump if positive
| 24	| JNE	| 0x01	0x10	| 0x18	| Jump if negative
| 25	| JZE	| 0x01	0x08	| 0x19	| Jump if zero
| 26	| TAB	| 0x0C	0x00	| 0x1A	| Transfers A to B
| 27	| TBA	| 0x13	0x00	| 0x1B	| Transfers B to A

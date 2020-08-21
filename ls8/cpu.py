"""CPU functionality."""

import sys

LDI = 0b10000010 # same as LDI = 130
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ir = [0] * 256
        self.mar = 0
        self.mdr = 0
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.ram = [0] * 256
        self.fl = [0] * 8
        self.running = False


    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        with open(f'ls8/examples/{filename}') as file:
            for line in file:
                instr = line.strip()
                instr = instr.split('#')
                if instr[0] != '':
                    as_int = int(instr[0], 2)
                    as_bin = bin(as_int)
                    self.ram[address] = as_int
                    address += 1

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            op_size = 1
            instr = self.ram[self.pc]
            if instr == LDI:
                reg_index = self.ram[self.pc + 1]
                self.mdr = self.ram[self.pc + 2]
                self.reg[reg_index] = self.mdr
                op_size += 2

            elif instr == PRN:
                reg_index = self.ram[self.pc + 1]
                print(self.reg[reg_index])
                op_size += 1

            elif instr == MUL:
                index_a = self.ram[self.pc + 1]
                index_b = self.ram[self.pc + 2]
                self.reg[index_a] *= self.reg[index_b]
                op_size += 2

            elif instr == ADD:
                #couldve used ALU for this
                op_size += 2
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.reg[reg_a] = self.reg[reg_a] + self.reg[reg_b]

            elif instr == PUSH:
                index_of_reg = self.ram[self.pc + 1]
                val = self.reg[index_of_reg]
                self.reg[7] -= 1
                self.ram[self.reg[7]] = val
                op_size += 1

            elif instr == POP:
                index_of_reg = self.ram[self.pc + 1]
                self.reg[index_of_reg] = self.ram[self.reg[7]]         
                self.reg[7] += 1
                op_size += 1

            elif instr == CALL:
                next_instr = self.pc + 2
                reg_index = self.ram[self.pc + 1]

                #need to push next instr to stack
                self.reg[7] -= 1
                self.ram[self.reg[7]] = next_instr

                self.pc = self.reg[reg_index]
                continue

            elif instr == RET:
                ret_addr = self.ram[self.reg[7]]
                self.pc = ret_addr
                continue

            elif instr == CMP:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                op_size += 2

                if self.reg[reg_a] == self.reg[reg_b]:
                    self.fl[5] = 0 #L flag
                    self.fl[6] = 0 #G flag
                    self.fl[7] = 1 #E flag
                elif self.reg[reg_a] > self.reg[reg_b]:
                    self.fl[5] = 0
                    self.fl[6] = 1
                    self.fl[7] = 0
                else:
                    self.fl[5] = 1
                    self.fl[6] = 0
                    self.fl[7] = 0

            elif instr == JMP:
                reg_index = self.ram[self.pc + 1]
                self.pc = self.reg[reg_index]
                continue

            elif instr == JNE:
                if self.fl[7] == 0:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                    continue

            elif instr == JEQ:
                if self.fl[7] == 1:
                    self.pc = self.reg[self.ram[self.pc + 1]]
                    continue

            elif instr == HLT:
                self.running = False

            self.pc += op_size
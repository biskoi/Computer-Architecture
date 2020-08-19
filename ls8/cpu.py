"""CPU functionality."""

import sys

LDI = 0b10000010 # same as LDI = 130
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ir = [0] * 256
        self.mar = 0
        self.mdr = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.running = False
        self.reg[7] = 0xF4


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

            elif instr == HLT:
                self.running = False

            self.pc += op_size
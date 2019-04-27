import os
from plugin import plugin

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@plugin("mips")
class MipsConverter:
    """
    Jarvis will convert any Assembly(mips) statement for you
    from assembly to machine code or from machine code(hex)
    to Assembly.

    Just write your command as follows:
    For Hex to Assembly:
        mips XXXXXXXX
        The above command calls mips with a 8 digit Hex code
        which makes a 32 bit instruction where the X are the
        Hex digits.

    For Assembly to Hex:
        mips Addi $t2, $t1, 0x12
        The above command calls mips with any mips basic instruction,
        in this case ADDI. There should be a space between the
        instruction keyword and the first register and then the
        rest can be separated with commas.

    A good practice would be to give a space between any separate part of
    the instruction such as between keyword and register, or keyword
    and immediate, or register and immediate.
    """

    def __call__(self, jarvis, s):
        if (s != ""):
            if (len(s) == 8 and s.find(" ") == -1):
                self.hexToAssembly(s, jarvis)
            else:
                self.assemblyToHex(s, jarvis)
        else:
            jarvis.say(
                "please enter a valid Assembly statement or a Machine code statement in Hex.")

    def __init__(self):
        # all lists which hold necessary info to interpret the command
        self.__com = []
        self.__form = []
        self.__inType = []
        self.__op = []
        self.__rs = []
        self.__rt = []
        self.__rd = []
        self.__shamt = []
        self.__func = []
        self.__imm = []

        self.__regName = []
        self.__regCode = []

        # populating the lists with info from the files
        commands = open(os.path.join(FILE_PATH, "../data/mips_coms.txt"), 'r')

        for line in commands:
            line = ''.join(line.split())

            self.__com.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__form.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__inType.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__op.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__rs.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__rt.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__rd.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__shamt.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__func.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__imm.append(line)

        commands.close()

        regs = open(os.path.join(FILE_PATH, "../data/mips_regs.txt"), 'r')

        for line in regs:
            line = ''.join(line.split())

            self.__regName.append(line[0:line.find('|')])
            line = line[line.find('|') + 1:]

            self.__regCode.append(line)

        regs.close()

    # To convert Hexadecimal to Binary
    def __hexToBin(self, myHex):
        binOfHex = ""
        for element in myHex:
            element = element.upper()
            if (element == "F"):
                binOfHex = binOfHex + "1111"
            elif (element == "E"):
                binOfHex = binOfHex + "1110"
            elif (element == "D"):
                binOfHex = binOfHex + "1101"
            elif (element == "C"):
                binOfHex = binOfHex + "1100"
            elif (element == "B"):
                binOfHex = binOfHex + "1011"
            elif (element == "A"):
                binOfHex = binOfHex + "1010"
            elif (element == "9"):
                binOfHex = binOfHex + "1001"
            elif (element == "8"):
                binOfHex = binOfHex + "1000"
            elif (element == "7"):
                binOfHex = binOfHex + "0111"
            elif (element == "6"):
                binOfHex = binOfHex + "0110"
            elif (element == "5"):
                binOfHex = binOfHex + "0101"
            elif (element == "4"):
                binOfHex = binOfHex + "0100"
            elif (element == "3"):
                binOfHex = binOfHex + "0011"
            elif (element == "2"):
                binOfHex = binOfHex + "0010"
            elif (element == "1"):
                binOfHex = binOfHex + "0001"
            elif (element == "0"):
                binOfHex = binOfHex + "0000"

        return binOfHex

    # To convert binary to hexadecimal
    def __binToHex(self, myBin):
        hexOfBin = ""
        for i in range(int(len(myBin) / 4)):
            newBin = myBin[i * 4:4 + i * 4]

            if (newBin == "1111"):
                hexOfBin = hexOfBin + "F"
            elif (newBin == "1110"):
                hexOfBin = hexOfBin + "E"
            elif (newBin == "1101"):
                hexOfBin = hexOfBin + "D"
            elif (newBin == "1100"):
                hexOfBin = hexOfBin + "C"
            elif (newBin == "1011"):
                hexOfBin = hexOfBin + "B"
            elif (newBin == "1010"):
                hexOfBin = hexOfBin + "A"
            elif (newBin == "1001"):
                hexOfBin = hexOfBin + "9"
            elif (newBin == "1000"):
                hexOfBin = hexOfBin + "8"
            elif (newBin == "0111"):
                hexOfBin = hexOfBin + "7"
            elif (newBin == "0110"):
                hexOfBin = hexOfBin + "6"
            elif (newBin == "0101"):
                hexOfBin = hexOfBin + "5"
            elif (newBin == "0100"):
                hexOfBin = hexOfBin + "4"
            elif (newBin == "0011"):
                hexOfBin = hexOfBin + "3"
            elif (newBin == "0010"):
                hexOfBin = hexOfBin + "2"
            elif (newBin == "0001"):
                hexOfBin = hexOfBin + "1"
            elif (newBin == "0000"):
                hexOfBin = hexOfBin + "0"
        return hexOfBin

    # convert decimal to binary
    def __decToBin(self, myDec):
        n = 0
        binOfDec = ""
        while myDec > 2**n:
            n = n + 1

        if (myDec < 2**n) & (myDec != 0):
            n = n - 1

        while n >= 0:
            if (myDec >= 2**n):
                myDec = myDec - 2**n
                binOfDec = binOfDec + "1"
            else:
                binOfDec = binOfDec + "0"
            n = n - 1

        return binOfDec

    # put the binary in multiples of 4
    def __nibbleEq(self, myBin):
        while (int(len(myBin) / 4) * 4 != len(myBin)):
            myBin = "0" + myBin
        return myBin

    # find the register from the given binary code
    def __findRegFromBin(self, regR, regName, regCode, jarvis):
        regCntr = 0
        flag = False
        reg = ""

        while (regCntr < len(regName)):
            if (regCode[regCntr] == regR):
                flag = True
                break
            regCntr = regCntr + 1

        if (flag is False):
            jarvis.say("Instruction is syntactically incorrect")
        else:
            reg = regName[regCntr]

        return reg

    # find the binary code of the given register
    def __getRegBin(self, regR, regName, regCode, jarvis):
        regCntr = 0
        flag = False
        regBin = ""

        while (regCntr < len(regName)):
            if (regName[regCntr] == regR):
                flag = True
                break
            regCntr = regCntr + 1

        if (flag is False):
            jarvis.say("Instruction is syntactically incorrect")
        else:
            regBin = regCode[regCntr]

        return regBin

    # find the first register given in the assembly command
    def __getRegFirst(self, assembly):
        temp = assembly[assembly.find(" ") + 1:]
        regR = temp
        if (temp.find(" ") != -1):
            regR = temp[0: temp.find(" ") + 1]
        regR = regR.strip()
        return regR

    # find the second register given in the assembly command
    def __getRegSecond(self, assembly):
        temp = assembly[assembly.find(" ") + 1:]
        temp = temp[temp.find(" ") + 1:]
        regR = temp
        if (temp.rfind(" ") != -1):
            regR = temp[0: temp.rfind(" ") + 1]
        regR = regR.strip()
        return regR

    # find the last register given in the assembly command
    def __getRegLast(self, assembly):
        if (assembly.rfind(" ") != -1):
            return assembly[assembly.rfind(" ") + 1:]
        else:
            return ""

    # Change assembly to Hex
    def assemblyToHex(self, assembly, jarvis):
        # bring the command into proper syntax
        assembly = assembly.replace(",", " ")
        assembly = " ".join(assembly.split())

        assBin = ""
        flag = False
        i = 0
        # find the level in the lists where the relevent command info lies
        while i < len(self.__com):
            comName = assembly.upper()
            if (assembly.find(" ") != -1):
                comName = (assembly[0: assembly.find(" ") + 1]).upper()
            comName = comName.strip()
            if (self.__com[i] == comName):
                flag = True
                break
            i = i + 1

        if (flag is False):
            jarvis.say("NO SUCH COMMAND IN ASSEMBLY")
            return
        else:
            jarvis.say("The format for this command is: "
                       + self.__com[i] + " " + self.__form[i])
            # append the opcode to the binary output
            assBin = assBin + self.__op[i]

            # To append rs register, if it is an R type instruction,
            if (self.__inType[i] == "R" and self.__rs[i] == "l"):
                regR = ""
                # these instructions have rs register at the end
                if ((self.__com[i] == "SLLV") or (self.__com[i]
                                                  == "SRAV") or (self.__com[i] == "SRLV")):
                    regR = self.__getRegLast(assembly)
                # instructions with no d register put rs in the front
                elif (self.__rd[i] != "l"):
                    regR = self.__getRegFirst(assembly)
                # the rest put rs in the middle of the first and last register
                else:
                    regR = self.__getRegSecond(assembly)

                assBin = assBin + \
                    self.__getRegBin(regR, self.__regName, self.__regCode, jarvis)
            # To append rs register, if it is an I type instruction,
            elif(self.__inType[i] == "I" and self.__rs[i] == "l"):
                regR = ""
                # these instructions have rs register in the middle of the
                # first and last register
                if ((self.__com[i] == "SLTI") or (self.__com[i]
                                                  == "SLTIU") or (self.__com[i] == "ORI")):
                    regR = self.__getRegSecond(assembly)
                elif((self.__com[i] == "ANDI") or (self.__com[i] == "ADDI")):
                    regR = self.__getRegSecond(assembly)
                # these instructions have a form imm(rs) which makes locating
                # rs easy
                elif (self.__form[i].find("(") != -1):
                    regR = assembly[assembly.find("(") + 1: assembly.find(")")]
                # the rest put rs in the beginning
                else:
                    regR = self.__getRegFirst(assembly)

                assBin = assBin + \
                    self.__getRegBin(regR, self.__regName, self.__regCode, jarvis)
            # if rs is niether of the above then rs code is already present in
            # the info
            elif (self.__rs[i] != "n"):
                assBin = assBin + self.__rs[i]

            # To append rt register, if it is an R type instruction,
            if (self.__inType[i] == "R" and self.__rt[i] == "l"):
                regR = ""
                # these instructions have rt in the middle of first and last
                # register
                if ((self.__com[i] == "SRA") or (self.__com[i]
                                                 == "SRL") or (self.__com[i] == "SRLV")):
                    regR = self.__getRegSecond(assembly)
                elif ((self.__com[i] == "SRAV") or (self.__com[i] == "SLL") or (self.__com[i] == "SLLV")):
                    regR = self.__getRegSecond(assembly)
                # the rest have rt at the end
                else:
                    regR = self.__getRegLast(assembly)

                assBin = assBin + \
                    self.__getRegBin(regR, self.__regName, self.__regCode, jarvis)
            # To append rt register, if it is an I type instruction,
            elif (self.__inType[i] == "I" and self.__rt[i] == "l"):
                regR = ""
                # these instructions have rt in the middle of first and last
                # register
                if ((self.__com[i] == "BEQ") or (self.__com[i] == "BNE")):
                    regR = self.__getRegSecond(assembly)
                # the rest have rt at the first pos
                else:
                    regR = self.__getRegFirst(assembly)

                assBin = assBin + \
                    self.__getRegBin(regR, self.__regName, self.__regCode, jarvis)
            # if rt is niether of the above then rt code is already present in
            # the info
            elif (self.__rt[i] != "n"):
                assBin = assBin + self.__rt[i]

            # To append rd register, if it is an R type instruction,
            if (self.__inType[i] == "R" and self.__rd[i] == "l"):
                assBin = assBin + \
                    self.__getRegBin(self.__getRegFirst(assembly), self.__regName, self.__regCode, jarvis)
            # rd code is already present in the info
            elif (self.__rd[i] != "n"):
                assBin = assBin + self.__rd[i]

            # if instruction is R type and shift amount is required
            if (self.__inType[i] == "R" and self.__shamt[i] == "l"):
                amt = self.__getRegLast(assembly)
                # handle if amount is in decimal
                if (amt.find("x") == -1 and amt != "" and amt.find("$") == -1):
                    if (len(self.__decToBin(amt)) > 5):
                        jarvis.say("Shift amount is too great")
                    amt = ("0" * (5 - len(self.__decToBin(amt)))) + \
                        self.__decToBin(int(amt))
                # handle if amount is in hex
                else:
                    if (len(self.__hexToBin(amt[2:])) > 5):
                        jarvis.say("Shift amount is too great")
                    amt = (
                        "0" * (5 - len(self.__hexToBin(amt[2:])))) + self.__hexToBin(amt[2:])
                assBin = assBin + amt
            # if instruction is R type and shift amount is not entered then it
            # is already present in the info
            elif (self.__inType[i] == "R"):
                assBin = assBin + self.__shamt[i]
            # always append the function is instruction is R type
            if (self.__inType[i] == "R"):
                assBin = assBin + self.__func[i]

            # immediate handeling
            if (self.__imm[i] == "l"):
                immB = ""

                if (assembly.find("(") == -1):
                    immB = self.__getRegLast(assembly)

                else:
                    immB = assembly[assembly.rfind(" "): assembly.find("(")]

                if (immB.find("x") == -1 and immB
                        != "" and immB.find("$") == -1):
                    immB = self.__decToBin(int(immB))

                else:
                    immB = self.__hexToBin(immB[2:])

                if (len(immB) > 16 and self.__inType[i] == "I"):
                    jarvis.say("Immediate is too large")

                elif (len(immB) > 26 and self.__inType[i] == "J"):
                    jarvis.say("Immediate is too large")
                else:
                    if (self.__inType[i] == "I"):
                        immB = ("0" * (16 - len(immB))) + immB
                    elif (self.__inType[i] == "J"):
                        immB = ("0" * (26 - len(immB))) + immB

                assBin = assBin + immB

        jarvis.say("Statement Type: " + self.__inType[i])
        if (self.__inType[i] == "R"):
            jarvis.say("opCode: " + assBin[0:6])
            jarvis.say("rs register: " + assBin[6:11])
            jarvis.say("rt register: " + assBin[11:16])
            jarvis.say("rd register: " + assBin[16:21])
            jarvis.say("Shift Amount: " + assBin[21:26])
            jarvis.say("Function: " + assBin[26:])
        elif (self.__inType[i] == "I"):
            jarvis.say("opCode: " + assBin[0:6])
            jarvis.say("rs register: " + assBin[6:11])
            jarvis.say("rt register: " + assBin[11:16])
            jarvis.say("immediate: 0x" + assBin[16:])
        elif (self.__inType[i] == "J"):
            jarvis.say("opCode: " + assBin[0:6])
            jarvis.say("immediate: 0x" + assBin[6:])

        jarvis.say("Statement in Hex: 0x" + self.__binToHex(assBin))

    # Change assembly to Hex
    def hexToAssembly(self, hexCommand, jarvis):

        assembly = ""
        command = self.__hexToBin(hexCommand)
        # the MSB 6 bits are the op code
        i = 0
        flag = False
        while (i < len(self.__op)):
            if ((self.__op[i] == command[0:6]) and (self.__op[i] != "000000")):
                flag = True
                break
            elif ((self.__func[i] == command[26:32]) and (self.__op[i] == "000000") and (command[0:6] == "000000")):
                flag = True
                break
            i = i + 1

        if (flag is False):
            jarvis.say("No such command exists.")
            return
        else:
            assembly = assembly + self.__com[i] + " "
            # compute the assembly instruction if instruction is R type
            if (self.__inType[i] == "R"):
                # handle d register first, d reg always comes first in the R
                # type instructions
                if (self.__rd[i] == "l"):
                    regR = command[16:21]
                    assembly = assembly + \
                        self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                # handle s register..
                if (self.__rs[i] == "l"):
                    if ((self.__com[i] == "SLLV") or (
                            self.__com[i] == "SRAV") or (self.__com[i] == "SRLV")):
                        regR = command[11:16]
                    else:
                        regR = command[6:11]

                    assembly = assembly + \
                        self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                # handle t registers..
                if (self.__rt[i] == "l"):
                    if ((self.__com[i] == "SLLV") or (
                            self.__com[i] == "SRAV") or (self.__com[i] == "SRLV")):
                        regR = command[6:11]
                    else:
                        regR = command[11:16]

                    assembly = assembly + \
                        self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                # handle shift amount
                if (self.__shamt[i] == "l"):
                    regR = "000" + command[21:26]
                    assembly = assembly + "0x" + self.__binToHex(regR)

            # compute the assembly instruction if instruction is I type
            elif (self.__inType[i] == "I"):
                # handle t registers
                if (self.__rt[i] == "l"):
                    if ((self.__com[i] == "BNE") or (self.__com[i] == "BEQ")):
                        regR = command[6:11]
                    else:
                        regR = command[11:16]

                    assembly = assembly + \
                        self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                # handle s registers
                if (self.__rs[i] == "l"):
                    if ((self.__com[i] == "BNE") or (self.__com[i] == "BEQ")):
                        regR = command[11:16]
                        assembly = assembly + \
                            self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                    elif (self.__form[i].find("(") != -1):
                        regR = command[16:]
                        assembly = assembly + "0x" + self.__binToHex(regR)

                    else:
                        regR = command[6:11]
                        assembly = assembly + \
                            self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + " "

                # handle immediate
                if (self.__imm[i] == "l"):
                    if (self.__form[i].find("(") != -1):
                        regR = command[6:11]
                        assembly = assembly + \
                            "(" + self.__findRegFromBin(regR, self.__regName, self.__regCode, jarvis) + ")"
                    else:
                        regR = command[16:]
                        assembly = assembly + "0x" + self.__binToHex(regR)

            # compute the assembly instruction if instruction is I type
            elif (self.__inType[i] == "J"):
                # only immediate there thus,
                regR = "00" + command[6:]
                assembly = assembly + "0x" + self.__binToHex(regR)
        jarvis.say(assembly)

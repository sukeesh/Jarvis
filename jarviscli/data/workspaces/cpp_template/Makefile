#This make file will compile your c++ program if your laptop supports make
#Use the command "make" to compile your program and "make clean" to remove it

CC:=g++ #Your chosen compiler
CFLAGS:= #Any compiler flags you choose
BIN:=out #The name of your output file
SRC:=hello_world.cpp #The name of your source code file

all: ${BIN}

${BIN}: ${SRC}
	@${CC} ${CFLAGS} -o $@ $^

clean:
	@rm -f ${BIN}
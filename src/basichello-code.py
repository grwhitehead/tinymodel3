from tinymodel3 import getRuntime
from tinymodel3_pybasic.program import Program

program = Program()
program.load("hello.bas")
program.execute()

getRuntime().wait()

from tinymodel3 import getRuntime
from tinymodel3_pybasic.interpreter import main

runtime = getRuntime()

# hack to simulate typing with a 200ms delay between characters. null characters are skipped over,
# resulting in a longer delay.
runtime.demoInput = "\0\0\0\0\0LOAD \"HELLO\"\n\0\0\0\0\0LIST\n\0\0\0\0\0RUN\n\0\0\0\0\0CLS\n\0\0\0\0\0LOAD \"DEMO1\"\n\0\0\0\0\0LIST\n\0\0\0\0\0RUN\n\0\0\0\0\0CLS\nLOAD \"DEMO2\"\n\0\0\0\0\0LIST\n\0\0\0\0\0RUN\n\0\0\0\0\0CLS\n\0\0\0\0\0LOAD \"DEMO3\"\n\0\0\0\0\0LIST\n\0\0\0\0\0RUN\n\0\0\0\0\0CLS\n\0\0\0\0\0LOAD \"DEMO4\"\n\0\0\0\0\0LIST\n\0\0\0\0\0RUN\n\0\0\0\0\0CLS\n"

main()

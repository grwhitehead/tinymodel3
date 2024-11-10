import tinymodel3

runtime = tinymodel3.Runtime()

pos = int(4*64+(64-21)/2)
runtime.print_at(pos, "TINY TRS-80 MODEL III")
runtime.delay(1250)
runtime.print_at(pos+64, "BY TREVOR FLOWERS")
runtime.delay(1250)
runtime.print_at(pos+64*2, "TRANSMUTABLE.COM")

runtime.wait()

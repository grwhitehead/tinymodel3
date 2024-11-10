import tinymodel3

runtime = tinymodel3.Runtime(32)

pos = int(4*32+(32-21)/2)
runtime.print_at(pos, "TINY TRS-80 MODEL III")
runtime.delay(1250)
runtime.print_at(pos+32, "BY TREVOR FLOWERS")
runtime.delay(1250)
runtime.print_at(pos+32*2, "TRANSMUTABLE.COM")

runtime.wait()

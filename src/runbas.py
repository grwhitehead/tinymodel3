import sys
from optparse import OptionParser
from tinymodel3_pybasic.program import Program

optparser = OptionParser("usage: %prog [options] file.bas ...")
optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
(opts, args) = optparser.parse_args()

for f in args:
    if opts.verbose:
        print(f, file=sys.stderr)
    
    program = Program()
    program.load(f)
    if opts.verbose:
        program.list()
    program.execute()

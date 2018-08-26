from common import Connective

def translate():
    formula = ''
    with open(r'C:\Users\Lior\university\אימות אוטומטי\project\benchmarks\schuppan\phltl\phltl_2_1.negated.pltl') as f:
        while True:
            # read next character
            char = f.read(1)
            # if not EOF, then at least 1 character was read, and
            # this is not empty
            if char:
                if char == '=':
                    char = f.read(1)
                    if char == '>':
                        formula += Connective.IMPLIES.value
                elif char == ' ':
                    continue
                else:
                    formula += char

            else:
                break
        print(formula)
translate()

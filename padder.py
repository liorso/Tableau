import os 

folder_path = "/home/asaf/Desktop/pltl/schuppan/phltl/"
output_folder = "/home/asaf/Desktop/pltl/schuppan_pad/phltl_pad/"


def pad_folder():

    for filename in os.listdir(folder_path):
        full_filename = str(folder_path)+str(filename)
        padded_formula = translate(full_filename)
        f = open(str(output_folder) + str(filename), "w+")
        f.write(padded_formula)
        f.close()


def translate(formula_file):
    formula = ''
    with open(formula_file) as f:
        while True:
            # read next character
            char = f.read(1)
            # if not EOF, then at least 1 character was read, and
            # this is not empty
            if char:
                if char == '=':
                    char = f.read(1)
                    if char == '>':
                        formula += ">"
                elif char == ' ':
                    continue
                elif char.islower():
                    padded_var = pad_var(f, char)
                    formula += padded_var
                else:
                    formula += char
            else:
                break
        return formula


def pad_var(f, first_char):
    init_pos = f.tell()
    
    next1 = f.read(1)
    if next1:
        if next1.isdigit():
            next2 = f.read(1)
            if next2:
                if next2.isdigit():
                    next3 = f.read(1)
                    if next3:
                        if next3.isdigit():
                            return str(first_char)+str(next1)+str(next2)+str(next3)
                        else:
                            f.seek(init_pos+2)
                            return str(first_char)+"0"+str(next1)+str(next2)
                    else:
                        f.seek(init_pos+2)
                        return str(first_char)+"0"+str(next1)+str(next2)
                else:
                    f.seek(init_pos+1)
                    return str(first_char)+"00"+str(next1)
            else:
                f.seek(init_pos+1)
                return str(first_char+"000")
        else:
            f.seek(init_pos)
            return str(first_char+"000")
    else:
        f.seek(init_pos)
        return str(first_char+"000")


pad_folder()

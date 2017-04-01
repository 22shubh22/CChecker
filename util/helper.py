import re
from store import (
    builtin_datatypes as bd
)

def parse_vars(program_instance):
    '''
    Takes a program instance and returns a dictionary containing all varibles
    within all functions
    along with their datatypes
    '''
    modifiers = r'(?P<mod>(const|auto|static|register|extern|volatile|signed|unsigned| )*)'
    fpattern = r'' + modifiers + '\s+(?P<type>' 
    spattern = ')\*{0,2}\s+.*?(?P<name>\w+)'
    for function in program_instance.functions:
        vars_dict = {}
        #text_lines = [text_line for text_line in function.text.split('\n') if text_line.strip()]
        for text_line in function.text:
            #print "text line:",text_line
            match = None
            for pos_dtype in bd:
                pattern = fpattern + pos_dtype + spattern
                match = re.search(pattern, text_line)
                if match:
                    break
            if not match:
                #print "Match not found"
                continue
            dtype = match.group('type')
            varname = match.group('name')
            #print "First var,dtype",varname,dtype
            unsigned = 0
            if match.group('mod') is not None and 'unsigned' in match.group('mod'):
                unsigned = 1
            vars_dict[varname] = (dtype, unsigned) # unsigned is 1 if dtype is unsigned, 0 otherwise
            csv = text_line.split(',')[1:]
            if csv:
                for declaration in csv:
                    pat = r'(?P<name>\w+).*'
                    match = re.search(pat, declaration)
                    vars_dict[match.group('name')] = (dtype, unsigned)
        function.vars = vars_dict

def parse_struct_vars(program_instance):
    '''
    Takes a program instance and returns a dictionary containing all varibles
    within all structures along with their datatypes
    '''
    modifiers = r'(?P<mod>(const|auto|static|register|extern|volatile|signed|unsigned| )*)'
    fpattern = r'' + modifiers + '\s+(?P<type>' 
    spattern = ')\*{0,2}\s+.*?(?P<name>\w+)'
    for struct in program_instance.structs:
        vars_dict = {}
        for text_line in struct.text:
            match = None
            for pos_dtype in bd:
                pattern = fpattern + pos_dtype + spattern
                match = re.search(pattern, text_line)
                if match:
                    break
            if not match:
                continue
            dtype = match.group('type')
            varname = match.group('name')
            unsigned = 0
            if match.group('mod') is not None and 'unsigned' in match.group('mod'):
                unsigned = 1
            vars_dict[varname] = (dtype, unsigned) # unsigned is 1 if dtype is unsigned, 0 otherwise
            csv = text_line.split(',')[1:]
            if csv:
                for declaration in csv:
                    pat = r'(?P<name>\w+).*'
                    match = re.search(pat, declaration)
                    vars_dict[match.group('name')] = (dtype, unsigned)
        struct.vars = vars_dict


def parse_union_vars(program_instance):
    '''
    Takes a program instance and returns a dictionary containing all varibles
    within all structures along with their datatypes
    '''
    modifiers = r'(?P<mod>(const|auto|static|register|extern|volatile|signed|unsigned| )*)'
    fpattern = r'' + modifiers + '\s+(?P<type>' 
    spattern = ')\*{0,2}\s+.*?(?P<name>\w+)'
    for union in program_instance.unions:
        vars_dict = {}
        for text_line in union.text:
            match = None
            for pos_dtype in bd:
                pattern = fpattern + pos_dtype + spattern
                match = re.search(pattern, text_line)
                if match:
                    break
            if not match:
                continue
            dtype = match.group('type')
            varname = match.group('name')
            unsigned = 0
            if match.group('mod') is not None and 'unsigned' in match.group('mod'):
                unsigned = 1
            vars_dict[varname] = (dtype, unsigned) # unsigned is 1 if dtype is unsigned, 0 otherwise
            csv = text_line.split(',')[1:]
            if csv:
                for declaration in csv:
                    pat = r'(?P<name>\w+).*'
                    match = re.search(pat, declaration)
                    vars_dict[match.group('name')] = (dtype, unsigned)
        union.vars = vars_dict


def parse_global_vars(program_instance):
    '''
    Takes a program instance and returns a dictionary containing all varibles
    within all structures along with their datatypes
    '''
    modifiers = r'(?P<mod>(const|auto|static|register|extern|volatile|signed|unsigned| )*)'
    fpattern = r'' + modifiers + '\s+(?P<type>' 
    spattern = ')\*{0,2}\s+.*?(?P<name>\w+)'
    vars_dict = {}
    for statement in program_instance.global_vars:
        match = None
        for pos_dtype in bd:
            pattern = fpattern + pos_dtype + spattern
            match = re.search(pattern, statement)
            if match:
                break
        if not match:
            continue
        dtype = match.group('type')
        varname = match.group('name')
        unsigned = 0
        if match.group('mod') is not None and 'unsigned' in match.group('mod'):
            unsigned = 1
        vars_dict[varname] = (dtype, unsigned)
        csv = statement.split(',')[1:]
        if csv:
            for declaration in csv:
                pat = r'(?P<name>\w+).*'
                match = re.search(pat, declaration)
                vars_dict[match.group('name')] = (dtype, unsigned)
    
    program_instance.global_vars_dict = vars_dict


condition_st = ('if', 'else if', 'while')
loops = ('for')

def conditions(pinst):
    ''''''
    res = []
    for func in pinst.functions:
        textlines = func.text
        st = func.start - 1
        for line in textlines:
            st += 1
            line = line.strip()
            #res.append(line)
            #match = re.search(r'(?P<type>\w*)\s*\(\s*(?P<cond>[\w\*\\+-=]*)\s*\).*', line)
            match = re.search(r'(?P<type>\w*)\s*\((?P<cond>.*?)\)', line)
            if not match:
                continue
            if match.group('type') in condition_st or match.group('type') in loops:
                ct = None
                if match.group('type') in condition_st:
                    ct = match.group('cond')
                elif match.group('type') == 'for':
                    ct = match.group('cond').split(';')[1]  # for loop only
                if ct and re.search(r'[\w ]+=[\w ]+', ct):
                    res.append(st+1) #exists
    return res

def parse_comments(pinst):
    '''
    Takes the programs and it will help in parsing the comments in lines
    '''
    
    for function in pinst.functions:
        orstart = function.start
        text_lines = function.text
        i = 0
        while i < len(text_lines):
            #i = i + 1
            #print str(i),':',line
            line = text_lines[i]
            if '//' in line:
                starts = i
                while line.endswith('\\\n'):
                    i = i + 1
                    line = text_lines[i]
                function.comments[function.start + starts] = text_lines[starts:i+1]
            if '/*' in line:
                starts = i
                #print 'Hey'
                while '*/' not in line:
                    i = i + 1 
                    line = text_lines[i]
                function.comments[function.start + starts] = text_lines[starts:i+1]
            i = i + 1

def find_goto(pinst):
    ''''''
    goto_list = []
    for function in pinst.functions:
        textlines = function.text
        st = function.start - 1
        pattern = r'(\W*)(goto|continue)(\b)(' ')?'
        for line in textlines:
            st += 1
            if re.search(pattern, line):
                goto_list.append(st + 1)
    return goto_list

def find_dynamic_memory_allocation(pinst):
    ''''''
    dynamic_list = []
    for function in pinst.functions:
        textlines = function.text
        st = function.start - 1
        pattern = r'(\W*)(malloc|calloc|realloc|free)(\b)(' ')?'
        for line in textlines:
            st += 1
            line = line.strip('\n')
            if re.search(pattern, line):
                dynamic_list.append(st+1)
    return dynamic_list

def comparison_floating(pinst):
    ''''''
    comp_op = ["==", "<=", ">=", "!=", "<", ">"]
    for func in pinst.functions:
        if func.vars is None:
            parse_vars(pinst)
        for line in func.text:
            if any(cmp in line for cmp in comp_op):
                line = line.strip()
                match = re.search(r'(?P<type>\w*)\s*\(\s*(?P<cond>.*)\s*\).*', line)
                if not match:
                    continue
                #print line
                if match.group('type') in condition_st:
                    res = re.search(r"(\w*\(\s*(?P<a>[\w\*\\+-]*)\s*((>=)|(>)|(<)|(<=)|(==)|(!=))\s*(?P<b>[\w\*\\+-]*)\s*\).*)", line)
                    if res:
                        pass
                        #print res.group('a'), res.group('b')
                elif match.group('type') in loops:
                    #print match.group('type')
                    cond = match.group('cond').split(';')[1]
                    res = re.search(r"(\s*(?P<a>[\w\*\\+-]*)\s*((>=)|(>)|(<)|(<=)|(==)|(!=))\s*(?P<b>[\w\*\\+-]*)\s*)", cond)
                    if res:
                        pass
                        #print res.group('a'), res.group('b')

def single_comments(pinst):
    ''''''
    res = []
    for comm in pinst.global_comments:
        text = comm.text[0].strip()
        lno = comm.start
        if text.startswith('//'):
            res.append(lno + 1)

    parse_comments(pinst)

    for fun in pinst.functions:
        #print fun.comments
        for lno in fun.comments:
            #print comm, lno
            text = fun.comments[lno][0].strip()
            #print lno, text
            if text.startswith('//'):
                res.append(lno + 1)

    return res

                



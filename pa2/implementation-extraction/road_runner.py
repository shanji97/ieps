from utils import *
import sys
sys.setrecursionlimit(4000)

def run_road_runner(first_html, second_html):
    first_wrapper = simplify(clean_html(remove_script(first_html)))
    first_wrapper_lines = first_wrapper.split("\n")
    second_html = simplify(clean_html(remove_script(second_html)))
    second_html = second_html.split("\n")
    a = match(first_wrapper_lines, second_html, [], 0, 0)
    return to_regex(a)
def is_opening(line):
    if isinstance(line,str):
        if line.startswith("</"):
            return False
        elif line.startswith("<"):
            return True
        return False
    return False

def is_closing(line):
    if isinstance(line,str):
        if line.startswith("</"):
            return True
        elif line.startswith("<"):
            return False
        return False
    return False

def find_end(wrapper, start):
    i = start
    while i < len(wrapper):
        if is_closing(wrapper[i]) and wrapper[i][2:] == wrapper[start][1:]:
            return i
        i += 1
    return -1

def find_start(wrapper, start):
    i = start
    while i>0:
        if is_opening(wrapper[i]) and wrapper[i][1:] == wrapper[start][2:]:
            return i
        i -= 1
    return -1

def get_tag(line):
    if is_opening(line):
        return line[1:-1]
    return line[2:-1]

def is_optional(line):
    if isinstance(line, str) and line.startswith("(opt)"):
        return True
    return False
                 
def combine_iterator(wrapper, iterator_tag, iterator):
    i = len(wrapper)-1
    end = None
    while i>0:
        while is_optional(wrapper[i]):
            i -= 1
        if is_closing(wrapper[i]) and get_tag(wrapper[i]) == get_tag(iterator_tag):
            while i>0:
                if is_opening(wrapper[i]) and get_tag(wrapper[i]) == get_tag(iterator_tag):
                    end = i
                    i -=1
                    break
                i -=1
        else:
            break
    if end is None:
        return wrapper
    
    wrapper = wrapper[:end]
    wrapper.append(iterator)
    return wrapper

def match(wrapper, sample, new_wrapper, start1, start2):
    if start1 >= len(wrapper) or start2 >= len(sample):
        return new_wrapper
    wrapper_line = wrapper[start1]
    sample_line = sample[start2]
    if wrapper_line == sample_line:
        new_wrapper.append(wrapper_line)
        return match(wrapper, sample, new_wrapper, start1+1, start2+1)
    elif wrapper_line != sample_line and not(wrapper_line.startswith("<") and sample_line.startswith("<")):
        new_wrapper.append(".*")
        return match(wrapper, sample, new_wrapper, start1+1, start2+1)
    else:
        #Tag missmatch: is iterator:
        terminal_wrapper = wrapper[start1-1]
        terminal_sample = sample[start2-1]
        found = False
        if is_closing(terminal_wrapper) and is_opening(wrapper_line) and  get_tag(terminal_wrapper) == get_tag(wrapper_line):
            end = find_end(wrapper, start1)
            if end != -1:
                start = find_start(wrapper, start1-1)
                if start != -1:
                    iter1 = wrapper[start:start1]
                    iter2 = wrapper[start1:end+1]
                    iterator = match(iter1, iter2, [], 0, 0)
                    if iterator is not None:
                        found = True
                        comb = combine_iterator(new_wrapper, terminal_wrapper, iterator)
                        a=0
                        return match(wrapper, sample, comb, end+1, start2)
        elif is_closing(terminal_sample) and is_opening(sample_line) and  get_tag(terminal_sample) == get_tag(sample_line):
            end = find_end(sample, start2)
            if end != -1:
                start = find_start(sample, start2-1)
                if start != -1:
                    iter1 = sample[start:start2]
                    iter2 = sample[start2:end+1]
                    iterator = match(iter1, iter2, [], 0, 0)
                    if iterator is not None:
                        found = True
                        comb = combine_iterator(new_wrapper, terminal_sample, iterator)
                        return match(wrapper, sample, comb, start1, end+1)
        #is optional
        if not found:
            i1 = 100000
            i2 = 100000
            for i in range(start1, len(wrapper)):
                if wrapper[i] == sample_line:
                    i1 = i
                    break
            for i in range(start2, len(sample)):
                if sample[i] == wrapper_line:
                    i2 = i
                    break  
            if i1 == i2:
                return None
            elif i1<i2:
                new_wrapper1 = new_wrapper.copy()
                for i in range(start1, i1):
                    new_wrapper1.append("(opt) ("+wrapper[i]+")?")
                f = match(wrapper, sample, new_wrapper1, i1, start2)
                if f is None and i2 != 100000:
                    for i in range(start2, i2):
                        new_wrapper.append("(opt) ("+sample[i]+")?")
                    f = match(wrapper, sample, new_wrapper, start1, i2)
                return f
            elif i1>i2:
                new_wrapper1 = new_wrapper.copy()
                for i in range(start2, i2):
                    new_wrapper1.append("(opt) ("+sample[i]+")?")
                f = match(wrapper, sample, new_wrapper1, start1, i2)
                if f is None and i1 != 100000:
                    for i in range(start1, i1):
                        new_wrapper.append("(opt) ("+wrapper[i]+")?")
                    f=match(wrapper,sample, new_wrapper, i1,start2)
                return f
        
def to_regex(iterator):
    output = "("
    for row in iterator:
        if isinstance(row, list):
            output += to_regex(row)
        else:
            output += row + "\n"
    return output + ")+"

first_html = open("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html", 'r').read()
second_html = open("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", 'r').read()
run_road_runner(first_html, second_html)



from utils import *
import re

def discovering_iterators(wrapper, sample, start1, start2):
    """
    Input:
    * Wrapper: document subset
    * Sample: document subset
    * start1: wrapper start position
    * start2: sample start position
    """
    iterators = None
    print(wrapper[start1-1])
    #Search wrapper
    a = side(wrapper, start1)
    if a is not None:
        return a
    #Search sample
    b = side(sample, start2)
    if b is not None:
        return (b[0], b[2], b[1], b[3])
    return None 

def side(wrapper, start1):
    if start1 > 0 and wrapper[start1-1].startswith(TAG):
        #last tag before mismatch
        terminal_tag = wrapper[start1-1].split(" ")[1]
        #Search wrapper
        end = -1
        count_same = 0
        count_opposite = 0
        opposite = False
        if terminal_tag.startswith("</"):
            opposite = True
        #Search for opposite tag
        for i in range(start1, len(wrapper)):
            if wrapper[i].startswith(TAG):
                row = " ".join(wrapper[i].split(" ")[1:])
                if row.startswith("</") == opposite:
                    count_same +=1
                    if count_opposite == count_same:
                        #Does the tag match
                        if row == terminal_tag:
                            end = i
                            break
                        else:
                            # is optional
                            break
                    elif count_same > count_opposite:
                        #is optional
                        break
                else:
                    count_opposite +=1
        iterators = None
        if end != -1:
            iterators = []
            # Match upward
            i1 = 0
            i2 = 0
            while 1+end-start1 > i2:
                # if lines are different and they are not string
                print(wrapper[start1-1-i1], wrapper[end-i2], wrapper[start1-1-i1].startswith(STRING), wrapper[end-i2].startswith(STRING))
                if wrapper[start1-1-i1] != wrapper[end-i2] and not (wrapper[start1-1-i1].startswith(STRING) and wrapper[end-i2].startswith(STRING)):
                    #If no iterators == optionals
                    print("##########")
                    print(wrapper[start1:end+1])
                    print(wrapper[:start1])
                    print("##########")
                    data = discovering_iterators(wrapper[start1:end+1][::-1], wrapper[:start1][::-1], i1, i2)

                    if data is not None:
                        iterator, d1, d2, d3 = data
                        i1 += d1
                        i2 += d2
                        #FIXME:
                        iterators = iterators[:-d3]
                        iterators.append(iterator[::-1])
                        #TODO: check if iterator appears next, compare generated iterator with next possible location
                        i2 = search_down(iterator, wrapper, end, i2)
                        i1 = search_down(iterator, wrapper, start1-1, i1)
                        #TODO: search up for iterators
                        continue
                    else:
                        #is optional
                        print("Optional: ", i1, i2)
                else:
                    if (wrapper[start1-1-i1].startswith(STRING) and wrapper[end-i2].startswith(STRING)) and wrapper[start1-1-i1] != wrapper[end-i2]:
                        iterators.append(STRING + " .*")
                    else:
                        iterators.append(wrapper[end-i2])
                i2 +=1
                i1 +=1
            return (iterators, 1+end-start1-i1, i2, i1)

def search_down(iterator, wrapper, end, i2):
    iterator2 = True
    while iterator2:
        # Iterator detected, search down for iterators
        print(to_regex(iterator))
        print("\n".join(wrapper[:end-i2 +1][::-1]))
        print()
        print("\n".join(wrapper[end-i2+1:]))
        data = re.compile(to_regex(iterator)).search("\n".join(wrapper[:end-i2 +1][::-1]))
        # data.span()[0] == 0
        if data is not None and data.span()[0] == 0:
            #FIXME: if pattern matches something too much ahead
            i2 += len((("\n".join(wrapper[:end-i2][::-1]))[:data.span()[1]]).split("\n")) -1
            continue
        else:
            #No more iterators
            return i2


def is_next_iterator(wrapper, start1):
    #last tag before mismatch
    terminal_tag = wrapper[start1-1].split(" ")[1]
    #Search wrapper
    end = -1
    count_same = 0
    count_opposite = 0
    opposite = False
    if terminal_tag.startswith("</"):
        opposite = True
    #Search for opposite tag
    for i in range(start1, len(wrapper)):
        if wrapper[i].startswith(TAG):
            row = " ".join(wrapper[i].split(" ")[1:])
            if row.startswith("</") == opposite:
                count_same +=1
                if count_opposite == count_same:
                    #Does the tag match
                    if row == terminal_tag:
                        end = i
                        break
                    else:
                        # is optional
                        break
                elif count_same > count_opposite:
                    #is optional
                    break
            else:
                count_opposite +=1
    return end


def to_regex(iterator):
    output = "("
    for row in iterator[::-1]:
        if isinstance(row, list):
            output += to_regex(row)
        else:
            if row.startswith(STRING):
                output += STRING + " .*\n"
            else:
                #output += " ".join(row.split(" ")[1:]) + " \n"
                output += row + "\n"
    return output[:-1] + ")+\n"


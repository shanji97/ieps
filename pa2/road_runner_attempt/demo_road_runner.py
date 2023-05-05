from match_lines import *
from utils import *

first_html = open("example1.html", 'r').read()
second_html = open("example2.html", 'r').read()

first_wrapper = generate_first_wrapper(clean_html(first_html))
open("example1_wrapper.html", 'w').write(first_wrapper)
open("example2_sample.html", 'w').write(clean_html(second_html))
first_wrapper_lines = first_wrapper.split("\n")

second_html = clean_html(second_html)

new_wrapper = ""
optional_element_first = ""
optional_first = False

wrapper_optional_depth = 0
sample_optional_depth = 0

def resolve_match(match_fun, found_mismatch, second_html, optional_element, optional_first, optional_element_first,
                  new_wrapper, wrapper_optional_depth):
    if found_mismatch:
        copy_second_html = second_html
        while not copy_second_html.startswith("</html>"):
            try:
                optional_element += copy_second_html.partition("\n")[0] + "\n"
                found_mismatch, copy_second_html, new_wrapper = \
                    match_fun(line_wrapper, copy_second_html, new_wrapper, i, optional_first)
                if not found_mismatch and wrapper_optional_depth == 0:  # found continuation
                    optional_first = False
                    second_html = copy_second_html
                    partition_wrapper = new_wrapper.rsplit("\n", 2)

                    pattern = r'\s+(\w+[-\w]*)\s*=\s*["\']([^"\']*)["\']'
                    matches = re.findall(pattern, optional_element)
                    for match in matches:
                        optional_element = optional_element.replace(match[1], "")

                    optional_element = optional_element.rsplit("\n", 2)[0]
                    if match_fun != match_string:
                        new_wrapper = partition_wrapper[0] + "\n(" + optional_element + ")?\n" + partition_wrapper[1] + "\n"
                    else:
                        new_wrapper = partition_wrapper[0] + "\n(.*)?\n" + partition_wrapper[1] + "\n"
                    break
                elif not found_mismatch and wrapper_optional_depth > 0:
                    if line_wrapper.startswith("</"):
                        wrapper_optional_depth -= 1

                    if wrapper_optional_depth == 0:
                        optional_element_first += line_wrapper
                        partition_wrapper = new_wrapper.rsplit("\n", 2)

                        if match_fun != match_string:
                            new_wrapper = partition_wrapper[0] + "\n(" + optional_element_first + ")?\n"
                        else:
                            new_wrapper = partition_wrapper[0] + "\n(.*)\n"

                        optional_element_first = ""
                        optional_first = False

            except IndexError:
                break
        if copy_second_html.startswith("</html>"):
            optional_element_first += line_wrapper
            if not line_wrapper.startswith("</") and not line_wrapper.endswith("/>") and line_wrapper.startswith("<"):
                wrapper_optional_depth += 1
            optional_first = True
            second_html = old_html
    else:
        if optional_first and wrapper_optional_depth == 0:
            partition_wrapper = new_wrapper.rsplit("\n", 2)

            if match_fun != match_string:
                new_wrapper = partition_wrapper[0] + "\n(" + optional_element_first + ")?\n" + partition_wrapper[1] + "\n"
            else:
                new_wrapper = partition_wrapper[0] + "\n(.*)\n" + partition_wrapper[1] + "\n"

            optional_element_first = ""
            optional_first = False
        elif optional_first and wrapper_optional_depth > 0:
            wrapper_optional_depth -= 1

    return second_html, optional_element, optional_first, optional_element_first, new_wrapper, wrapper_optional_depth


for i in range(len(first_wrapper_lines)):
    line_wrapper = first_wrapper_lines[i]

    if line_wrapper.startswith(TAG):
        line_wrapper = line_wrapper.replace(TAG + " ", "")
        optional_element = second_html.partition("\n")[0] + "\n"
        old_html = second_html

        found_mismatch, second_html, new_wrapper = \
            match_tag(line_wrapper, second_html, new_wrapper, i, optional_first)

        second_html, optional_element, optional_first, optional_element_first, new_wrapper, wrapper_optional_depth = \
            resolve_match(match_tag,
                          found_mismatch,
                          second_html,
                          optional_element,
                          optional_first,
                          optional_element_first,
                          new_wrapper, wrapper_optional_depth)

    elif line_wrapper.startswith(STRING):
        line_wrapper = line_wrapper.replace(STRING + " ", "")
        old_html = second_html
        found_mismatch, second_html, new_wrapper = \
            match_string(line_wrapper, second_html, new_wrapper, i, optional_first)

        second_html, optional_element, optional_first, optional_element_first, new_wrapper, wrapper_optional_depth = \
            resolve_match(match_string,
                          found_mismatch,
                          second_html,
                          optional_element,
                          optional_first,
                          optional_element_first,
                          new_wrapper, wrapper_optional_depth)

    elif line_wrapper.startswith(REGGEX):
        line_wrapper = line_wrapper.replace(REGGEX + " ", "")
        old_html = second_html
        found_mismatch, second_html, new_wrapper = \
            match_regex(line_wrapper, second_html, new_wrapper, i, optional_first)

        second_html, optional_element, optional_first, optional_element_first, new_wrapper, wrapper_optional_depth = \
            resolve_match(match_regex,
                          found_mismatch,
                          second_html,
                          optional_element,
                          optional_first,
                          optional_element_first,
                          new_wrapper, wrapper_optional_depth)

print(new_wrapper)

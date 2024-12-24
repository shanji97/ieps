from utils import *

first_html = open("pages/example1.html", 'r').read()
second_html = open("pages/example2.html", 'r').read()

first_wrapper = generate_first_wrapper(clean_html(first_html))
open("pages/example1_wrapper.html", 'w').write(first_wrapper)
first_wrapper_lines = first_wrapper.split("\n")

second_html = clean_html(second_html)

attribute_regex = r'\s*(\w+(?:-\w+)*)\s*=\s*["\']([^"\']*)["\']'
new_wrapper = ""
for i in range(len(first_wrapper_lines)):
    wrapper_line = first_wrapper_lines[i]
    if wrapper_line.startswith(TAG):
        wrapper_line = wrapper_line.replace(TAG + " ", "")

        line_sample = second_html.partition("\n")[0]
        first_attrs = set(re.findall(attribute_regex, wrapper_line))
        second_attrs = set(re.findall(attribute_regex, line_sample))
        if first_attrs != second_attrs:
            print("MISMATCH - TAG - at wrapper line " + str(i+1) + ": " + str(first_attrs ^ second_attrs))
            new_wrapper += "TAG MISMATCH " + wrapper_line
        else:
            new_wrapper += wrapper_line

        second_html = second_html.replace(line_sample + "\n", "", 1)
    elif wrapper_line.startswith(STRING):
        wrapper_line = wrapper_line.replace(STRING + " ", "")

        line_sample = second_html.partition("\n")[0]
        if wrapper_line != line_sample:
            print("MISMATCH - STRING - at wrapper line " + str(i+1) + ": " + wrapper_line + " - " + line_sample, i)
            new_wrapper += "STRING MISMATCH " + wrapper_line + "\n"
        else:
            new_wrapper += wrapper_line

        second_html = second_html.replace(line_sample + "\n", "", 1)
    elif wrapper_line.startswith(REGGEX):
        wrapper_line = wrapper_line.replace(REGGEX + " ", "")
        try:
            regex = re.compile(wrapper_line.strip())
        except re.error:
            regex = re.compile(re.escape(wrapper_line.strip()))
        match_1 = regex.search(second_html)
        if match_1:
            second_html = regex.sub("", second_html, 1).strip()
            new_wrapper += wrapper_line
        else:
            print("MISMATCH - REGGEX - at wrapper line " + str(i+1) + ": " + regex.pattern)
            new_wrapper += "REGGEX MISMATCH " + regex.pattern + "\n"

    new_wrapper += "\n"

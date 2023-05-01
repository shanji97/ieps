import time

from utils import *

audi_html = clean_html(open("pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html"))
# print(audi_html)
# audi_html = clean_html(open("pages/overstock.com/jewelry01.html", encoding='iso-8859-1').read())

# print(audi_html)

# for i in range(len(audi_lines)):
#

# d = ">"
# for line in audi_lines:
#     s = [e+d for e in line.split(d) if e]
#     for i in range(len(s)):
#         new_audi_html += s[i].strip() + "\n"
# print(new_audi_html)

audi_lines = audi_html.splitlines()
volvo_lines = volvo_html.splitlines()
#
attribute_regex = r'\s*(\w+(?:-\w+)*)\s*=\s*["\']([^"\']*)["\']'
#
for i in range(min(len(audi_lines), len(volvo_lines))):
    if audi_lines[i] != volvo_lines[i]:
        # first_attrs = set(re.findall(attribute_regex, audi_lines[i]))
        # second_attrs = set(re.findall(attribute_regex, volvo_lines[i]))
        # # first_value =
        # if first_attrs != second_attrs:
        print("Line", i)
        print("Audi:", audi_lines[i])
        print("Volvo:", volvo_lines[i])
        # print("Difference:", first_attrs ^ second_attrs)
        print()

print(time.time() - start)

cleaned_audi_file = open("pages/audi_cleaned.html", "w")
cleaned_audi_file.write(str(audi_html))
cleaned_audi_file.close()
cleaned_volvo_file = open("pages/volvo_cleaned.html", "w")
cleaned_volvo_file.write(str(volvo_html))
cleaned_volvo_file.close()

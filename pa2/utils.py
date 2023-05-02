import re

REGGEX = "<REGGEX>"
TAG = "<TAG>"
STRING = "<STRING>"


def clean_html(html):
    new_html = ""
    for i in range(len(html) - 1):
        if html[i] == ">" or html[i + 1] == "<":
            new_html += html[i] + "\n"
        else:
            new_html += html[i]
    new_html += html[-1]
    new_html = new_html.splitlines()
    new_html = [line for line in new_html if (line and not line.isspace())]

    new_html_joined = []
    i = 0
    while i < len(new_html) - 1:
        tag_name = re.match(r'<\s*([a-zA-Z0-9]+).*?>', new_html[i])
        if tag_name:
            tag_name = tag_name.group(1)
        if tag_name and new_html[i].startswith(("<" + tag_name)) and new_html[i + 1] in ["</" + tag_name + ">"]:
            new_html_joined.append(new_html[i] + new_html[i + 1])
            i += 2
        else:
            new_html_joined.append(new_html[i])
            i += 1
    new_html_joined.append(new_html[-1])

    new_html = "\n".join(new_html_joined)

    return new_html


def generate_first_wrapper(cleaned_html):
    pattern_script = r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>'
    pattern_style = r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>'
    pattern_comment = r'<!--(.*)-->'

    cleaned_html = re.sub(pattern_script, REGGEX + ' <script(?s:.)*?<\/script>', cleaned_html)
    cleaned_html = re.sub(pattern_style, REGGEX + ' <style(?s:.)*?<\/style>', cleaned_html)
    cleaned_html = re.sub(pattern_comment, REGGEX + ' <!--(?s:.)*?-->', cleaned_html)

    cleaned_lines = cleaned_html.split("\n")
    tagged_lines = ""
    for line in cleaned_lines:
        if line.startswith(REGGEX):
            tagged_lines += line
        elif line.startswith("<") and line.endswith(">"):
            tagged_lines += TAG + " " + line
        else:
            tagged_lines += STRING + " " + line
        tagged_lines += "\n"

    return tagged_lines

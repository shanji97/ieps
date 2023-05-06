import re

from bs4 import BeautifulSoup

REGGEX = "<REGGEX>"
TAG = "<TAG>"
STRING = "<STRING>"


def clean_html(html):
    # standardize attribute positions
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    soup = BeautifulSoup(html, "lxml")

    for x in soup.find_all():
        if (len(x.get_text(strip=True)) == 0 and x.name not in ['img']) or \
                x.name in ['script', 'style', 'meta', 'link', 'iframe']:
            x.extract()

    html = str(soup)
    new_html = ""
    for i in range(len(html) - 1):
        if html[i] == ">" or html[i + 1] == "<":
            new_html += html[i] + "\n"
        else:
            new_html += html[i]
    new_html += html[-1]
    new_html = new_html.splitlines()
    new_html = [line.strip() for line in new_html if (line and not line.isspace())]

    new_html = "\n".join(new_html)

    return new_html


def generate_first_wrapper(cleaned_html):
    # pattern_script = r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>'
    # pattern_style = r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>'
    # pattern_iframe = r'<iframe\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/iframe>'
    pattern_comment = r'<!--(.*)-->'
    # pattern_meta = r'<meta.*>'
    # pattern_link = r'<link.*>'
    #
    # cleaned_html = re.sub(pattern_script, '', cleaned_html)
    # cleaned_html = re.sub(pattern_style, '', cleaned_html)
    cleaned_html = re.sub(pattern_comment, '', cleaned_html)
    # cleaned_html = re.sub(pattern_meta, '', cleaned_html)
    # cleaned_html = re.sub(pattern_link, '', cleaned_html)
    # cleaned_html = re.sub(pattern_iframe, '', cleaned_html)

    # cleaned_html = re.sub(pattern_script, REGGEX + r' \\A(<script(?s:.)*?<\/script>)', cleaned_html)
    # cleaned_html = re.sub(pattern_style, REGGEX + r' \\A(<style(?s:.)*?<\/style>)', cleaned_html)
    # cleaned_html = re.sub(pattern_comment, REGGEX + r' \\A(<!--(?s:.)*?-->)', cleaned_html)

    cleaned_lines = cleaned_html.split("\n")
    cleaned_lines = [line for line in cleaned_lines if (line and not line.isspace())]
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

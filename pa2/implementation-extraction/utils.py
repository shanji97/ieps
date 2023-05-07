import re
from bs4 import BeautifulSoup, Comment

def simplify(html):
    new_html = ""
    for line in html.split("\n"):
        if line.startswith("<"):
            simple = line.split(" ")
            if simple[0].endswith(">"):
                new_html += simple[0] + "\n"
            else:
                new_html += simple[0] + ">\n"
        else:
            new_html += line + "\n"
    return new_html

def remove_script(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
    
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    
    return str(soup)

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

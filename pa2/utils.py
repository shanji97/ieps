import re

from bs4 import Comment, BeautifulSoup


def clean_html(html):

    soup = BeautifulSoup(html, features='lxml')
    for s in soup.select('script'):
        s.replace_with(soup.new_tag('script', type='text/javascript'))
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for c in comments:
        c.replace_with(soup.new_tag('div', **{'class': 'html_comment'}))
    for s in soup.select('style'):
        s.replace_with(soup.new_tag('style', type='text/css'))
    cleaned_soup_html = str(BeautifulSoup(str(soup), features='lxml'))

    new_html = ""
    for i in range(len(cleaned_soup_html) - 1):
        if cleaned_soup_html[i] == ">" or cleaned_soup_html[i + 1] == "<":
            new_html += cleaned_soup_html[i] + "\n"
        else:
            new_html += cleaned_soup_html[i]
    new_html += cleaned_soup_html[-1]
    new_html = new_html.splitlines()
    new_html = [line for line in new_html if line]

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

import re
import json
import html2text
def regex_extraction(page, page_content):
    page_object = {}
    regex_list = []
    if page == 'rtvslo':
        regex_list = [
            (r"<h1>(.*)</h1>", "Title"),
            (r"<div class=\"subtitle\">(.*)</div>", "SubTitle"),
            (r"<p class=\"lead\">(.*)</p>", "Lead"),
            (r"<div class=\"author-name\">(.*)</div>", "Author"),
            (r"<div class=\"publish-meta\">\n\t\t(.*)<br>", "PublishedTime"),
            (r"<div class=\"article-body\">(.*?)<div class=\"gallery\">", "Content")
        ]

        for regex, key in regex_list:
            pattern = re.compile(regex)
            match = re.findall(pattern, page_content)
            if match:
                page_object[key] = match[0]

        html_parser = html2text.HTML2Text()
        html_parser.ignore_links = True
        html_parser.ignore_images = True
        content = html_parser.handle(page_object["Content"]).replace("\n", " ")
        page_object["Content"] = content

        return json.dumps(page_object, indent=4, ensure_ascii=False)

    elif page == 'overstock':
        regex_list = [
        (r"<td><a href=\"http://www\.overstock\.com/cgi-bin/d2\.cgi\?PAGE=PROFRAME[\w\W]*?\"><b>(.*?)</b>", "Title"),
        (r"<s>(.*?)</s>", "List price"),
        (r"<span class=\"bigred\"><b>(.*?)</b>", "Price"),
        (r"<b>You Save:[\w\W]*?class=\"littleorange\">(.*?)</span>", "Saving"),
        (r"<span class=\"normal\">(.*?)</span>", "Content")
    ]

    html_parser = html2text.HTML2Text()
    html_parser.ignore_links = True
    html_parser.ignore_images = True
    json
    for match in zip(*(re.findall(pattern, page_content, re.DOTALL) for pattern, _ in regex_list)):
        json_object = dict(zip((key for _, key in regex_list), match))
        json_object["Saving percent"] = json_object["Saving"].split(" ")[1]
        json_object["Saving"] = json_object["Saving"].split(" ")[0]
        json_object["Content"] = html_parser.handle(json_object["Content"]).replace("\n", "")
        print(json.dumps(json_object, indent=4, ensure_ascii=False))
        
        
    elif page =='studentska_prehrana':
    
    else:
        return None
    
    return page_object
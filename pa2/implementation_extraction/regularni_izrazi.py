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
            (r"<div class=\"publish-meta\">\n\t\t(.*)<br>", "PublishedTime")
        ]

        content_regex = r"<div class=\"article-body\">(.*?)<div class=\"gallery\">"

        if "Content" in page_object:
            page_content = page_object["Content"]
            pattern = re.compile(content_regex, re.DOTALL)
            match = re.findall(pattern, page_content)
            if match:
                page_object["Content"] = match[0]
                html_parser = html2text.HTML2Text()
                html_parser.ignore_links = True
                html_parser.ignore_images = True
                content = html_parser.handle(page_object["Content"]).replace("\n", " ")
                page_object["Content"] = content

            for regex, key in regex_list:
                pattern = re.compile(regex)
                match = re.findall(pattern, page_content)
                if match:
                    page_object[key] = match[0]

            print(json.dumps(page_object, indent=4, ensure_ascii=False))
                    
        
        # regex_list = [
        #     (r"<h1>(.*)</h1>", "Title"),
        #     (r"<div class=\"subtitle\">(.*)</div>", "SubTitle"),
        #     (r"<p class=\"lead\">(.*)</p>", "Lead"),
        #     (r"<div class=\"author-name\">(.*)</div>", "Author"),
        #     (r"<div class=\"publish-meta\">\n\t\t(.*)<br>", "PublishedTime"),
        #     (r"<div class=\"article-body\">(.*?)<div class=\"gallery\">", "Content")
        # ]

        # for regex, key in regex_list:
        #     pattern = re.compile(regex)
        #     match = re.findall(pattern, page_content)
        #     if match:
        #         page_object[key] = match[0]

        #     html_parser = html2text.HTML2Text()
        #     html_parser.ignore_links = True
        #     html_parser.ignore_images = True
        #     content = html_parser.handle(page_object["Content"]).replace("\n", " ")
        #     page_object["Content"] = content
        #     print(json.dumps(page_object, indent=4, ensure_ascii=False))

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
        jsons = []
        for match in zip(*(re.findall(pattern, page_content, re.DOTALL) for pattern, _ in regex_list)):
            json_object = dict(zip((key for _, key in regex_list), match))
            json_object["Saving percent"] = json_object["Saving"].split(" ")[1]
            json_object["Saving"] = json_object["Saving"].split(" ")[0]
            json_object["Content"] = html_parser.handle(json_object["Content"]).replace("\n", "")
            print(json.dumps(json_object, indent=4, ensure_ascii=False))
    elif page =='studentska_prehrana':
        regex_list = [
        (r"<h3 class=\"no-margin bold\">(.*?)</h3>", "Title"),
        (r"<small>(.*?)</small>[\w\W]*", "Address"),
        (r"<span class=\" color-light-grey\">(.*?)</span>", "Price"),
        (r"<span class=\" color-light-grey\">(.*?)<\/span>\s*<\/small>", "List price"),
        (r"<div class=\"col-md-12 text-bold\">(.*?)</div>", "Work time"),
        (r"<strong class=\" color-blue\">(.*?)</strong>", "Main dish"),
        (r"<ul class=\"list-unstyled\">(?:\s*<li>.*?</li>){1}\s*<li>.*?<i>(.*?)</i>", "Salad"),
        ]

        html_parser = html2text.HTML2Text()
        html_parser.ignore_links = True
        html_parser.ignore_images = True
        for match in zip(*(re.findall(pattern, page_content, re.DOTALL) for pattern, _ in regex_list)):
            json_object = dict(zip((key for _, key in regex_list), match))
            json_object["Main dish"] = html_parser.handle(json_object["Main dish"]).replace("&nbsp;","")
            json_object["Work time"] = html_parser.handle(json_object["Work time"]).replace("\n", "").replace("\t","").replace("<br>","")
            print(json.dumps(json_object, indent=4, ensure_ascii=False))
        else:
            return None
    
    return page_object
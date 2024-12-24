import selenium
import json
import html2text
from lxml import html


def xpath_extraction(page, page_content):
    siteString = html.fromstring(page_content)
    page_object = {}
    common_path = '/html/body/'
    error = False
    if page == 'rtvslo':
        for key, xpath in {
            "Title": '//*[@id="main-container"]/div[3]/div/header/h1',
            "SubTitle": '//*[@id="main-container"]/div[3]/div/header/div[2]',
                        "Lead": '//*[@id="main-container"]/div[3]/div/header/p',
                        "Author": '//*[@id="main-container"]/div[3]/div/div[1]/div[1]/div',
                        "PublishedTime": '//*[@id="main-container"]/div[3]/div/div[1]/div[2]/text()[1]',
                        "Content": '//*[@id="main-container"]/div[3]/div/div[2]/article',
        }.items():
            element = siteString.xpath(xpath)
            if element:
                page_object[key] = element[0].text_content().strip().replace("\t", "").replace("\n", "")

    elif page == 'overstock':
        jsons = []
        for i in range(1, len(3)):
            common_path = f'{common_path}table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]'
            try:
                data = {}
                for key, xpath in {
                    "Title": f'{common_path}/a/b',
                    "List price": f'{common_path}/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s',
                    "Price": f'/{common_path}/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b',
                    "Saving": f'{common_path}/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span',
                    "Content": '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/table/tbody/tr/td[2]/span/text()'
                }.items():
                    element = siteString.xpath(xpath)
                    if element:
                        data[key] = element[0].text_content().strip().replace(
                            "\t", "").replace("\n", "")
                    jsons.append(data)
            except:
                if error:
                    break
                else:
                    error = True
                None
            page_content = json.dumps(jsons, indent=4, ensure_ascii=False)
    elif page == 'studentska_prehrana':
        jsons = []
        for i in range(1, len(100)):
            common_path = f'{common_path}div[3]/div[2]'
            try:
                data = {}
                for key, xpath in {
                    "Locale name": f'{common_path}/div[1]/div[1]/div[2]/div[1]/h3[1]',
                    "Address": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[1]',
                    "Price": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[2]',
                    "List price": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[4]',
                    "Work time": f'{common_path}/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]',
                    "Main dish": f'//strong[@class="color-blue"][{i}]',
                    "Salad": f'//ul[@class="list-unstyled"][{i}]/li[2]/i[1]'
                }.items():
                    element = siteString.xpath(xpath)
                    if element:
                        data[key] = element[0].text_content().strip().replace("\t", "").replace("\n", "").replace("&nbsp;","")
                    jsons.append(data)
            except:
                if error:
                    break
                else:
                    error = True
                None
            page_content = json.dumps(jsons, indent=4, ensure_ascii=False)
    else:
        return None

    return page_object

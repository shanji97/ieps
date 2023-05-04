import selenium
import json
import html2text
from lxml import html


def xpath_extraction(page, page_content):
    siteString = html.fromstring(page_content)
    page_object={}
    if page =='rtvslo':
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
            
    elif page =='overstock':
        jsons = []
        for i in range(1, len(3)):
            base_xpath = f'/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]'
            try:
                data = {}
                for key, xpath in {
                    "Title": f'{base_xpath}/a/b',
                    "List price": f'{base_xpath}/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s',
                    "Price": f'/{base_xpath}/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b',
                    "Saving": f'{base_xpath}/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span',
                    "Content": '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/table/tbody/tr/td[2]/span/text()'
                }.items():
                    element = siteString.xpath(xpath)
                    if element:
                        data[key] = element[0].text_content().strip().replace("\t", "").replace("\n", "")
                    jsons.append(data)
            except:
                None
            page_content = json.dumps(jsons, indent=4, ensure_ascii=False)
    elif page == 'studentska_prehrana':
        jsons = []
        header_base= f'/html/body/div[3]/div[2]'
        for i in range(1, len(100)):
            base_xpath = f'/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]'
            try:
                data = {}
                for key, xpath in {
                    "Locale name":'/html[1]/body[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/h3[1]',
                    "Address":'/html[1]/body[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/small[1]',
                    "Price": '/html[1]/body[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/small[2]/span[2]',
                    "List price": '/html[1]/body[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/small[2]/span[4]',
                    "Work time":  '/html[1]/body[1]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]',
                    "Main dish": f'/html[1]/body[1]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[{i}]/div[1]/div[1]/div[1]/h5[1]/strong[1]',
                    "Salad": f'/html[1]/body[1]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[{1}]/div[1]/div[1]/ul[1]/li[2]/i[1]'
                }.items():
                    element = siteString.xpath(xpath)
                    if element:
                        data[key] = element[0].text_content().strip().replace("\t", "").replace("\n", "")
                    jsons.append(data)
            except:
                None
            page_content = json.dumps(jsons, indent=4, ensure_ascii=False)
    else:
        return None
    
    return page_object
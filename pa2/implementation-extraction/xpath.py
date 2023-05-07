import json
from lxml import html


def single_value(site_string, xpath_string):
    return site_string.xpath(xpath_string)[0].text_content().strip().replace("\t", "").replace("\n", "").replace("&nbsp;", "").replace(" ()", "")


def xpath_extraction(page, page_content):
    site_string = html.fromstring(page_content)
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
            element = site_string.xpath(xpath)
            if element:
                page_object[key] = element[0].text_content(
                ).strip().replace("\t", "").replace("\n", "")
        print(p)
    elif page == 'overstock':
        jsons = []
        common_path = f'{common_path}table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]'
        data = {}
        for key, xpath in {
            "Title": f'{common_path}/a/b',
            "List price": f'{common_path}/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s',
            "Price": f'/{common_path}/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b',
            "Saving": f'{common_path}/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span',
            "Content": '/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/table/tbody/tr/td[2]/span/text()'
        }.items():
            element = site_string.xpath(xpath)
            if element:
                data[key] = element[0].text_content().strip().replace(
                    "\t", "").replace("\n", "").replace(" ", "")
                jsons.append(data)
                print(json.dumps(jsons, indent=4, ensure_ascii=False))

    elif page == 'studentska_prehrana':
        jsons = []
        common_path = f'{common_path}div[3]/div[2]'
        data = {}
        # #Static "one time  data."
        data['Locale name'] = single_value(
            site_string, f'{common_path}/div[1]/div[1]/div[2]/div[1]/h3[1]')
        data['Address'] = single_value(
            site_string, f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[1]')
        data['Price'] = single_value(
            site_string, f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[2]')
        data['List price'] = single_value(
            site_string, f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[4]')
        data['Work time'] = single_value(
            site_string, f'{common_path}/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]')  # need combining with regex to arhieve bese result
        data['Salad'] = single_value(
            site_string, '//ul[@class="list-unstyled"][1]/li[2]/i[1]')
        data['Main dish'] = single_value(
            site_string, f'//strong[@class=" color-blue"][1]')
        print(json.dumps(data, indent=4, ensure_ascii=False))
        
        # for i in range(1, 5): #Kako ugotoviti, na mesto, da dati kar neko cifro.
        #     dish = f'//strong[@class=" color-blue"][1]' # Zakaj samo i=1 nekaj izpiše?
        #     salad = f'//ul[@class="list-unstyled"][1]/li[2]/i[1]'
        #     data = {}
        #     for key, xpath in {
        #         "Locale name": f'{common_path}/div[1]/div[1]/div[2]/div[1]/h3[1]',
        #         "Address": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[1]',
        #         "Price": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[2]',
        #         "List price": f'{common_path}/div[1]/div[1]/div[2]/div[1]/small[2]/span[4]',
        #         "Work time": f'{common_path}/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[2]/div[1]',
        #         "Main dish": dish,
        #         "Salad": salad
        #     }.items():
        #         element = site_string.xpath(xpath)

        #         print(xpath)
        #         if element:
        #             data[key] = element[0].text_content().strip().replace(
        #                 "\t", "").replace("\n", "").replace("&nbsp;", "").replace(" ()", "")
        #     print(json.dumps(data, indent=4, ensure_ascii=False)) #Kak pretvoriti v en json objekt in ne v več?

    else:
        return None

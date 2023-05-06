import sys
import regularni_izrazi
import xpath

extraction_algorithm = 'B'
rtv_page_1 = open(
    "../pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html").read()
rtv_page_2 = open(
    "../pages/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html").read()

overstock_page_1 = open("../pages/overstock.com/jewelry01.html").read()
overstock_page_2 = open("../pages/overstock.com/jewelry02.html").read()

studentska_prehrana_page_1 = open(
    "../pages/studentska-prehrana.si/- Študentska prehrana.html").read()
studentska_prehrana_page_2 = None

if extraction_algorithm == "A":  # regex
    regularni_izrazi.regex_extraction("rtvslo", rtv_page_1)
    regularni_izrazi.regex_extraction("rtvslo", rtv_page_2)
    regularni_izrazi.regex_extraction("overstock", overstock_page_1)
    regularni_izrazi.regex_extraction("overstock", overstock_page_2)
    regularni_izrazi.regex_extraction("studentska_prehrana", studentska_prehrana_page_1)

elif extraction_algorithm == "B":  # xpath
    # rtv_slo_extracted_data_xpath_1 = xpath.xpath_extraction(
    #     "rtvslo", rtv_page_1)
    # rtv_slo_extracted_data_xpath_2 = xpath.xpath_extraction(
    #     "rtvslo", rtv_page_2)
    xpath.xpath_extraction(
        "overstock", overstock_page_1)
    xpath.xpath_extraction(
        "overstock", overstock_page_2)
    xpath.xpath_extraction(
        "studentska_prehrana", studentska_prehrana_page_1)

    print(rtv_slo_extracted_data_xpath_1)
elif extraction_algorithm == "C":  # road runner
    pass
else:
    print("Invalid extraction algorithm")
    sys.exit(1)

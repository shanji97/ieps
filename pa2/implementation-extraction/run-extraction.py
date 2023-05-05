import sys
import regularni_izrazi
import xpath

extraction_algorithm = sys.argv[1]

rtv_page_1 = open(
    "input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html").read()
rtv_page_2 = open(
    "input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html").read()

overstock_page_1 = open("input-extraction/overstock.com/jewelry01.html").read()
overstock_page_2 = open("input-extraction/overstock.com/jewelry02.html").read()

studentska_prehrana_page_1 = open("input-extraction/studentska-prehrana.si/- Študentska prehrana.html").read()
studentska_prehrana_page_2 = None

if extraction_algorithm == "A":  # regex
    rtv_slo_extracted_data_regex_1 = regularni_izrazi.regex_extraction("rtvslo", rtv_page_1)
    rtv_slo_extracted_data_regex_2 = regularni_izrazi.regex_extraction("rtvslo", rtv_page_2)
    overstock_extracted_data_regex_1 = regularni_izrazi.regex_extraction("overstock", overstock_page_1)
    overstock_extracted_data_regex_2 = regularni_izrazi.regex_extraction("overstock", overstock_page_2)
    studentska_prehrana_extracted_data_regex_1 = regularni_izrazi.regex_extraction("studentska_prehrana", studentska_prehrana_page_1)

    print(rtv_slo_extracted_data_regex_1)
elif extraction_algorithm == "B":  # xpath
    rtv_slo_extracted_data_xpath_1 = xpath.xpath_extraction("rtvslo", rtv_page_1)
    rtv_slo_extracted_data_xpath_2 = xpath.xpath_extraction("rtvslo", rtv_page_2)
    overstock_extracted_data_xpath_1 = xpath.xpath_extraction("overstock", overstock_page_1)
    overstock_extracted_data_xpath_2 = xpath.xpath_extraction("overstock", overstock_page_2)
    studentska_prehrana_extracted_data_xpath_1 = xpath.xpath_extraction("studentska_prehrana", studentska_prehrana_page_1)

    print(rtv_slo_extracted_data_xpath_1)
elif extraction_algorithm == "C":  # road runner
    pass
else:
    print("Invalid extraction algorithm")
    sys.exit(1)
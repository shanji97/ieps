import sys
import regularni_izrazi
import xpath
import road_runner

extraction_algorithm = sys.argv[1]

rtv_page_1 = open(
    "../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html").read()
rtv_page_2 = open(
    "../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html").read()

overstock_page_1 = open(
    "../input-extraction/overstock.com/jewelry01.html").read()
overstock_page_2 = open(
    "../input-extraction/overstock.com/jewelry02.html").read()

studentska_prehrana_page_1 = open(
    "../input-extraction/studentska-prehrana.si/- Študentska prehrana.html").read()
studentska_prehrana_page_2 = open(
    "../input-extraction/studentska-prehrana.si2/- Študentska prehrana.html").read()

if extraction_algorithm == "A":  # regex
    print('Rtv slo')
    print('=====================================================================')
    regularni_izrazi.regex_extraction("rtvslo", rtv_page_1)
    regularni_izrazi.regex_extraction("rtvslo", rtv_page_2)
    print('Overstock')
    print('=====================================================================')
    regularni_izrazi.regex_extraction("overstock", overstock_page_1)
    regularni_izrazi.regex_extraction("overstock", overstock_page_2)
    print('Študentska prehrana')
    print('=====================================================================')
    regularni_izrazi.regex_extraction("studentska_prehrana", studentska_prehrana_page_1)
    regularni_izrazi.regex_extraction("studentska_prehrana", studentska_prehrana_page_2)

elif extraction_algorithm == "B":  # xpath
    print('Rtv slo')
    print('=====================================================================')
    xpath.xpath_extraction("rtvslo", rtv_page_1)
    xpath.xpath_extraction("rtvslo", rtv_page_2)
    print('Overstock')
    print('=====================================================================')
    xpath.xpath_extraction("overstock", overstock_page_1)
    xpath.xpath_extraction("overstock", overstock_page_2)
    print('Studentska prehrana.')
    print('=====================================================================')
    xpath.xpath_extraction("studentska_prehrana", studentska_prehrana_page_1)
    xpath.xpath_extraction("studentska_prehrana", studentska_prehrana_page_2)

elif extraction_algorithm == "C":  # road runner
    rtv_regex = road_runner.run_road_runner(rtv_page_1, rtv_page_2)
    overstock_regex = road_runner.run_road_runner(overstock_page_1, overstock_page_2)
    studentska_prehrana_regex = road_runner.run_road_runner(studentska_prehrana_page_1, studentska_prehrana_page_2)

    print('Rtv slo')
    print('=====================================================================')
    print(road_runner.run_road_runner(rtv_page_1, rtv_page_2))
    print('Overstock')
    print('=====================================================================')
    print(road_runner.run_road_runner(overstock_page_1, overstock_page_2))
    print('Studentska prehrana.')
    print('=====================================================================')
    print(road_runner.run_road_runner(studentska_prehrana_page_1, studentska_prehrana_page_2))

else:
    print("Invalid extraction algorithm")
    sys.exit(1)

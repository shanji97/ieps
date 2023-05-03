from utils import *

html_audi_file = open("pages/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
cleaned_file_output = open("pages/audi_cleaned.html", "w")

cleaned_audi_html = clean_html(html_audi_file)

cleaned_file_output.write(cleaned_audi_html)
cleaned_file_output.close()

import re
attribute_regex = r'\s*(\w+(?:-\w+)*)\s*=\s*["\']([^"\']*)["\']'


def match_string(line_wrapper, second_html, new_wrapper, i, optional_first):
    mismatch_found = False
    line_sample = second_html.partition("\n")[0]

    if line_wrapper != line_sample:
        print("MISMATCH - STRING - at wrapper line " + str(i + 1) + ": " + line_wrapper + " - " + line_sample)

        mismatch_found = True
    else:
        new_wrapper += line_wrapper + "\n"

    second_html = second_html.replace(line_sample + "\n", "", 1)
    return mismatch_found, second_html, new_wrapper


def match_tag(line_wrapper, second_html, new_wrapper, i, optional_first):
    mismatch_found = False
    line_sample = second_html.partition("\n")[0]
    tag_sample_name = re.findall('<(?:[\/!])*(\w+)(?:[\s\/]|>)', line_wrapper)
    wrapper_sample_name = re.findall('<(?:[\/!])*(\w+)(?:[\s\/]|>)', line_sample)

    is_closing_wrapper = line_wrapper.startswith("</")
    is_closing_sample = line_sample.startswith("</")


    if is_closing_wrapper == is_closing_sample and tag_sample_name and wrapper_sample_name:
        if tag_sample_name[0] != wrapper_sample_name[0]:
            print("MISMATCH - TAG name - at wrapper line " + str(
                i + 1) + ": " + tag_sample_name[0] + " - " + wrapper_sample_name[0])
            # new_wrapper += "TAG name MISMATCH " + line_wrapper
            mismatch_found = True
        else:
            first_attrs = set(re.findall(attribute_regex, line_wrapper))
            second_attrs = set(re.findall(attribute_regex, line_sample))
            if first_attrs != second_attrs:
                print("MISMATCH - TAG attrs - at wrapper line " + str(i + 1) + ": " + str(first_attrs ^ second_attrs))
                # new_wrapper += "TAG attrs MISMATCH " + line_wrapper
                mismatch_found = True
            else:
                new_wrapper += line_wrapper + "\n"
    else:
        print("MISMATCH - TAG closing - at wrapper line " + str(i + 1) + ": " + line_wrapper + " - " + line_sample)
        mismatch_found = True
    second_html = second_html.replace(line_sample + "\n", "", 1)

    return mismatch_found, second_html, new_wrapper


def match_regex(line_wrapper, second_html, new_wrapper, i, optional_first):
    mismatch_found = False
    line_sample = second_html.partition("\n")[0]

    try:
        regex = re.compile(line_wrapper.strip())
    except re.error:
        regex = re.compile(re.escape(line_wrapper.strip()))
    match_1 = regex.search(second_html)
    if match_1:
        second_html = regex.sub("", second_html, 1).strip()
        new_wrapper += line_wrapper + "\n"
    else:
        # new_wrapper += "REGGEX MISMATCH " + regex.pattern
        mismatch_found = True


    return mismatch_found, second_html, new_wrapper

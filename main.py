from os.path import split
from re import match

import pdfplumber
from email.policy import strict
from fileinput import close
import pandas as pd
from collections import namedtuple
import re


#create namedtuple to help create a dataframe using Pandas later it has fields: course_code , grades and academic_term
Record = namedtuple('Record', 'banner_id course_code grades academic_term gpa')

#function to convert pdf to text
def pdf_to_text (pdf_file: str) -> [str]:
    with pdfplumber.open(pdf_file) as pdf:
        pdf_text = []
        for page in pdf.pages:
            #content = page.extract_text()
            pdf_text.append(page.extract_text())
            #print(f"Page {page_number + 1}:\n{content}\n")
        return pdf_text

if __name__ == '__main__':
    extracted_text = pdf_to_text("transcript.pdf")
    i = 0 #to count how many lines. Maybe print it later to check or compare?
    #this is to print the whole extracted text from the pdf
    for text in extracted_text:
        #print(text)
        i+=1
    print(f"-------------------------------------------------{i}")
    i = 0

    #define variables for regex expressions for each pattern we want to extract to add to the re.compile later
    re_banner_id = r"(B00[0-9]{6})|"
    #re_course_name = r"([A-Z]{4} [ED] \d{4}) ([AB0-9]{0,3} .*)|"
    re_course_name = r"([A-Z]{4}) ([ED]) (\d{4}) .*? (PASS|[ABCDF][+-]?)+\s|"
    re_semester = r"(\d{4}/\d{4} [A-Za-z]+)|"
    re_gpa = r"(Term: (\d\.\d{2}) Cumulative: (\d\.\d{2}))"
    pattern1 = re.compile(re_banner_id + re_course_name + re_semester + re_gpa)
    # pattern1 = re.compile(r"([A-Z]{4} [ED] \d{4}) ([AB0-9]{0,3} .*)|(\d{4}/\d{4} [A-Za-z]+)|((Term: |Cumulative: )\d\.\d{2})")

    items_mining = [] #this to save the regexed text as namedtuple
    regex_lines = [] #to save regexed text in list
    for page in extracted_text:
        matches = pattern1.finditer(page)
        for match in matches:
            #print(type(match))
            print(match.group())
            regex_lines.append(match.group())
            #vars to prepare each of the namedtuple fields with the specified group
            #print(f"{match.group(1)} , {match.group(2)} , {match.group(3)} , {match.group(4)}")
            banner_id = match.group(1) if match.group(1) is not None else ""
            course_code = match.group(2) + " " + match.group(4) if match.group(2) is not None and match.group(4) is not None else ""
            grades = match.group(5) if match.group(5) is not None else ""
            academic_term = match.group(6) if match.group(6) is not None else ""
            gpa = match.group(7) if match.group(7) is not None else ""

            items_mining.append(Record(banner_id, course_code, grades, academic_term, gpa))
            #print(academic_term)

    print(f"---------------------------------------------{items_mining[20].grades} {items_mining[20].course_code} {len(items_mining)}-----------------------------------------------------------")
    # for i in regex_lines:
    #     print(i)
    #
    df = pd.DataFrame(items_mining)
    #df.to_csv('employe.csv', index=False)
    # for row in df.itertuples():
    #     print(row[1])
    # tmp = ""
    # collected = []
    # for i, row in enumerate(df.itertuples()):
    #     if tmp == row[1]:
    #        print(f"Something is worng: {row[1]}")
    #        collected.append(i)
    #     tmp = row[1]
    # df.drop(collected, inplace=True)
#
    #
    # pd.set_option('display.max_rows',None)
    # pd.set_option('display.max_columns', None)

    print(df['course_code'].to_string())
    #print(df.to_string())

    # solve the probelm of accesing row i in course code column it will help us to === level 1000 to make changes

    df2 = pd.read_csv('Book1.csv')
    df2.loc[44, 'Course'] = "NoTOtalHHHHHHHHHHH"
    print(df2['Course'].to_string())

    passed_courses = []
    for index, value in enumerate(df2.itertuples()):
        x = value[5]
        for i in df['course_code']:
            if i != "" and i == x:
                print(f"You have taken : {x} course !!!!!!{index}")
                passed_courses.append(index)

    for i in range(len(passed_courses)):
        print(type(df2.loc[3,'Mark']))
        df2.loc[passed_courses[i],'Mark'] = "DONE!"
    df2.to_csv('Modified_Book1.csv', index=False)

    # for value in df2.itertuples():
    #     x = value[5]
    #     xx = "1000"
    #     for indx, i in enumerate(df['course_code']):
    #         if i:
    #             y = i[indx]
    #             print(f"{x} {value.__contains__(xx)} {y}")


    #print(df2.iloc[:,[4]])
    # for i in range(5):
    #     print(df.loc[0])
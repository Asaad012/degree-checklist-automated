from os.path import split
from re import match
from xml.etree.ElementTree import tostring

import pdfplumber
from email.policy import strict
from fileinput import close
import pandas as pd
from collections import namedtuple
import re


#create namedtuple to help create a dataframe using Pandas later it has fields: course_code , grades and academic_term
Record = namedtuple('Record', 'banner_id course_code grades academic_term gpa')

#function to convert pdf to text and return that text as list
def pdf_to_text (pdf_file: str) -> [str]:
    with pdfplumber.open(pdf_file) as pdf:
        pdf_text = []
        for page in pdf.pages:
            pdf_text.append(page.extract_text())
        return pdf_text

def check_scienceWithLab (curr_course) -> bool:
    science_with_lab_list = ["CSCI 1107", "CSCI 1109", "CSCI 1108", "BIOL 1010", "BIOL 1011", "CHEM 1011", "CHEM 1012",
                        "ENGI 1103", "ERTH 1080", "PHYC 1190", "PHYC 1290", "PHYC 1310", "PHYC 1320", "PSYO 1011",
                        "PSYO 1012", "PSYO 1031", "PSYO 1032"]
    for lab in science_with_lab_list:
        if lab == curr_course:
            return True
    return False

def check_humanities (curr_course) -> bool:
    human_social_list = ["ARBC","ARCH","ASSC","BIOT","CANA","CHIN","CLAS","CPST","CTMP","CRWR","EMSP","ENGL","EURO",
                         "FREN","GWST","GERM","HIST","HSTC","INTD","ITAL","JOUR","KING","LAWS","LEIS","MUSC","PHIL",
                         "POLI","RELS","RUSN","SLWK","SOSA","SPAN","SUST","THEA", "HPRO"]
    for course_list in human_social_list:
        if course_list in curr_course:
            return True

    return False
def check_business (curr_course) -> bool:
    business_list = ["COMM","MGMT","BIOC","BIOL","CHEM","ERTH","ECON","MARA","MATH","STAT","MEDS","MICI","OCEA","PSYO","NESC",
                     "PHYC","ENGI","BIOE","BMNG","CHEE","CIVL","ECED","ENGM","ENGN","ENVE","ENG ","INWK","MATL","MECH","MINE","PEAS","PETR",]
    for course_in_list in business_list:
        if course_in_list in curr_course:
            return True

    return False

if __name__ == '__main__':
    extracted_text = pdf_to_text("transcript.pdf")

    #this is to print the whole extracted text from the pdf
    for text in extracted_text:
        print(text)
    print(f"-------------------------------------------------")

    #define variables for regex expressions for each pattern we want to extract to add to the re.compile later
    re_banner_id = r"(B00[0-9]{6})|"
    #re_course_name = r"([A-Z]{4} [ED] \d{4}) ([AB0-9]{0,3} .*)|" #oroginal catch which worked also for course name and code
    re_course_name = r"([A-Z]{4}) ([A-Z]{1}) (\d{4}) .*? (PASS|[ABCDF][+-]?)+\s|" # ex: (CSCI) (E or D, will be ignored later) (2110) anything (PASS | A+)
    re_semester = r"(\d{4}/\d{4} [A-Za-z]+)|"
    re_gpa = r"(Term: (\d\.\d{2}) Cumulative: (\d\.\d{2}))"

    pattern1 = re.compile(re_banner_id + re_course_name + re_semester + re_gpa)
    # pattern1 = re.compile(r"([A-Z]{4} [ED] \d{4}) ([AB0-9]{0,3} .*)|(\d{4}/\d{4} [A-Za-z]+)|((Term: |Cumulative: )\d\.\d{2})")#u can write it this way as well(looks bad right?)

    items_mining = [] #this to save the regexed match text as namedtuple
    #loop to extract the patterns catched from each page of the pdf
    for page_indx in extracted_text:
        matches = pattern1.finditer(page_indx)
        for match in matches:
            print(match.group())

            #vars to prepare each of the namedtuple fields with the specified group
            banner_id = match.group(1) if match.group(1) is not None else ""
            #note here we escaped group(3) bc basically we dont want it in the column (it was in the middle between two string we want to catch and ignore the middle)
            course_code = match.group(2) + " " + match.group(4) if match.group(2) is not None and match.group(4) is not None else ""
            grades = match.group(5) if match.group(5) is not None else ""
            academic_term = match.group(6) if match.group(6) is not None else ""
            gpa = match.group(7) if match.group(7) is not None else ""

            items_mining.append(Record(banner_id, course_code, grades, academic_term, gpa)) #we append to the list item that is namedtuple Record to easy access later
            #print(academic_term)

    print(f"----------------------------------------------------------------------------------------------------")

    filtered_transcript_df = pd.DataFrame(items_mining) # dt -> dataframe using pandas for the list items_mining
    #df.to_csv('employe.csv', index=False) # generate employe.csv that file that will have

    #modify the academic term to make it written in the same row of each course ... this will make our process later easy
    check_term = ""
    for i, term in enumerate(filtered_transcript_df['academic_term']):
        if term != "":
            check_term = filtered_transcript_df.loc[i,'academic_term']
        filtered_transcript_df.loc[i, 'academic_term'] = check_term

    #print(filtered_transcript_df['course_code'].to_string()) # print the column course_code
    print(filtered_transcript_df.to_string()) #print the whole df

    # read degree checklist file of type CSV using pandas library, and make sure NaN values are escaped
    degree_checklist_df = pd.read_csv('Book1.csv', keep_default_na=False)
    #degree_checklist_df.loc[44, 'Course'] = "NoTOtalHHHHHHHHHHH" #just to try how changing a column is possible
    print(degree_checklist_df['Course'].to_string()) #print the column Course

    passed_courses = []#save indexes of the passed courses se we can later update other columns in the sam row of the passed course like check complete
    uncatched_courses = []
    i = 0
    for index, course in enumerate(filtered_transcript_df['course_code']):
        if course == "":
            continue
        for j, course2 in enumerate(degree_checklist_df['Course']):
            if "level" in course2 or "Other" in course2 or "TOTAL" in course2 or course2 == "":  # saving time from looping when the line we are in is not a course name
                continue
            if len(degree_checklist_df.loc[j, 'Mark']) > 0 or "/" in degree_checklist_df.loc[j, 'Term']:
                continue

            if ((course2 == course or course == degree_checklist_df.loc[j,'Equivalent']) or ("Science with Lab: " in course2 and check_scienceWithLab(course))
                    or ("Humanities" in course2 and check_humanities(course)) or ("Business" in course2 and check_business(course))):
                grade = filtered_transcript_df.loc[index, 'grades']
                if grade == "F" or grade == "C-" or grade == "D":
                    degree_checklist_df.loc[j, 'Notes'] += f"Failed: {course} "
                    break
                degree_checklist_df.loc[j, 'Mark'] = filtered_transcript_df.loc[index, 'grades']
                degree_checklist_df.loc[j, 'Term'] = filtered_transcript_df.loc[index, 'academic_term']
                print(f"You have taken : {course} course !!!!!!{j} {index} {degree_checklist_df.loc[j,'Equivalent']} {filtered_transcript_df.loc[index, 'grades']} {i}")
                passed_courses.append(index)
                i+=1
                break

    for i in uncatched_courses:
        print(f"-->>>>> {i}")
    print(degree_checklist_df.to_string())

    #check_scienceWithLab(uncatched_courses, degree_checklist_df)
    #loop through the list of saved indexes/positions of the passed courses and modify the data to check passed courses and etc
    for i in range(len(passed_courses)):
        #print(f"{type(degree_checklist_df.loc[3, 'Mark'])}")
        degree_checklist_df.loc[passed_courses[i], 'Mark'] = "DONE!"

    degree_checklist_df.to_csv('Modified_Book1.csv', index=False)


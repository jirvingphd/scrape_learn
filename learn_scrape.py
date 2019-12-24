import requests
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import numpy as  np
import requests
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd


def start_driver(url = 'https://instruction.learn.co/staff/students'):
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    return driver


def load_login_data(login_data_file = "/Users/jamesirving/.secret/learn_login.json",
                   verbose=True):
    """Loads in json file from path"""
    with open(login_data_file,'r+') as f:
        import json
        fdata= f.read()
        login_data =  json.loads(fdata)
        
        if verbose:
            print("Loaded json data. Keys:")
            print(login_data.keys())
        return login_data
    
    
    
def github_login(driver,login_data=None):
    """Logs into GitHub Account (for instruction.learn)
    url = 'https://instruction.learn.co/staff/students'
    """
    if login_data is None:
        login_data= load_login_data()
        
    username = driver.find_element_by_xpath('//*[@id="login_field"]')
    username.send_keys(login_data['username'])

    password = driver.find_element_by_xpath('//*[@id="password"]')
    password.send_keys(login_data['password'])

    sign_in = driver.find_element_by_xpath('//*[@id="login"]/form/div[2]/input[8]')
    sign_in.click()
    
def instruct_menu_to_cohort_roster(driver,cohort="pt"):
    import time
    time.sleep(0.5)
    
    cohort_lead =driver.find_element_by_xpath('/html/body/div[1]/nav/div[1]/ul/li[1]/a')
    my_cohorts = driver.find_element_by_xpath('//*[@id="js-parentDropdownLink"]')
    if cohort=="pt":
        cohort_link = driver.find_element_by_xpath('//*[@id="js-childrenList-141"]/ul/li[1]/a')

    elif cohort=="ft":
        cohort_link = driver.find_element_by_xpath('//*[@id="js-sidenavChildrenList-140"]/li[2]/a')
#         return ft_cohort

    actions = ActionChains(driver)
    actions.move_to_element(cohort_lead)
    actions.pause(.5)
    actions.click(my_cohorts)
    actions.pause(.5)

    actions.click(cohort_link)
    return actions.perform()


def cohort_driver_to_csv(driver,output_file='cohort_output.csv',
                         debug=False,load=False,
                        load_kws=None):
    """Exports the table content inside of the driver.page_source to csv file.
    
    Args:
        driver (WebDriver): cohort instruct page's driver
        output_file (str): name of csv file to save.
    
    TO DO: Add link extraction"""
    my_html = driver.page_source
    soup = BeautifulSoup(my_html, 'html.parser')

    table = soup.find("table")
    rows = table.find_all('tr')

    output_rows = []
    for row in rows:
        row_text = row.get_text(separator='\t',strip=True)
        
        if "Links" in row_text:
            row_text=row_text.replace("\tLinks",' ')
        
        profile_links = [x['href'] for x in row.find_all('a')]#
        if debug:
            print(len(row_text.split('t')))
            if 'John' in row_text:
                print("Returning John row object")
                return row
            
        repl_dict={
            ':':' ',
#             ')':' ',
            '\n':' '
        }
        for k,v in repl_dict.items():
            row_text = row_text.replace(k,v)
#         row_text = row_text.replace(':',' ').replace(')',' ').replace('\n',' ')

        output_rows.append(row_text)#row.get_text(separator='\t',strip=True))

    with open(output_file, 'w+') as csvfile:
        csvfile.write('\n'.join(output_rows))
        
    print(f"[i] Successfully saved '{output_file}'")
    
    if load:
#         header = pd.read_csv(output_file,delimiter='\t',nrows=1)
        if load_kws is not None:
            df = pd.read_csv(output_file,delimiter='\t',**load_kws)
        else:
            df = pd.read_csv(output_file,delimiter='\t')
         
        ## Save column names to restore
#         cols = df.columns
        df.reset_index(inplace=True)
        cols = df.drop('index',axis=1).columns
        
        if df["Completed Lessons"].isna().any():
            shift_index = df.loc[(df['Completed Lessons'].isna())].index#.copy()
            
#             ## Preview bad row alignment
#             display(df.loc[shift_index])
            
            ## Replace the column data to match others
            cols_to_swap = {"Completed Lessons":"Last Checkin Note",
                           "Instructor":"Checkins (NoShows)",
                           "Checkins (NoShows)":"Last Checkin Note"}
            
            for bad_col,good_col in cols_to_swap.items():
#             df.loc[shift_index,'Completed Lessons']=df.loc[shift_index,'Last Checkin Note'].copy()
                df.loc[shift_index,bad_col]=df.loc[shift_index,good_col].copy()
            df.loc[shift_index,"Last Checkin Note"]=np.nan
        
        
#             ##Preview changes
#             display(df.loc[shift_index])
        
        
        
        # Drop one of the redundant columns
        drop_col = "Completed Lessons"#'Last Checkin Note'
        df.drop(columns=[drop_col],inplace=True)

        # Restore names to columns
        df.columns = cols
        
        return df
    
    
    
def help():
    print("[i] Workflow:")
    print("driver = start_driver()")
    print('login_data=load_login_data()')
    print("github_login(driver,login_data)")
    print("instruct_menu_to_cohort_roster(driver,cohort='pt')")
    print("df = cohort_driver_to_csv(driver,'pt_cohort_data.csv',load=True)")
help()


###########
import re

def BOOKMARK():
    print("This function is just a bookmark for VS Code's OUTINE VIEW")


def get_student_info_from_full_url(driver,full_url):
    """Get the `uk-card-body` text from student's instruction.learn full url"""
    driver.get(full_url)
    my_html = driver.page_source
    student_soup = BeautifulSoup(my_html, 'html.parser')
    tag = student_soup.find('div',attrs={'class':'uk-card-body'})
    student_info = tag#.text
    print('Function used to return the .text, now it returns the tag itself.')
    return student_info


def make_instructor_learn_url(partial_url):
    """Prepends the base url to relative url for df.apply"""
    base_url = 'https://instruction.learn.co' + partial_url
    return base_url


import re
def get_urls_from_custom_badges(student_info_card):
    """Accepts the student_info card from instruction.learn
    profile.  Retreives the urls from the custom-badges div."""
    links = student_info_card.find_all('a',href=True)
    # learn_url = links[1]['href']


    ## List of Links 
    student_links = dict(
        slack_url = [links[0]['href']],
        learn_url = [links[1]['href']],
        github_url = [links[2]['href']],
        mailto_url = [links[3]['href']],
        projects_url = [links[4]['href']], 
        grad_dash_url = [links[5]['href']])
    
    return student_links


def get_student_dict_from_student_info(student_info_tag):
    """Uses regex to parse info from student's
    instruction.learn.co/staff/students/____ page:
    

    Ex Use:
    full_link = df['full_url'].iloc[i]
    student_info_tag =  get_student_info_from_full_url(full_link)
    
    student_dict = get_student_dict_from_student_info(student_info_tag)
    """
    student_info = student_info_tag.text

    import re

    student_dict = {}
    
    ## Get urls
    student_urls= get_urls_from_custom_badges(student_info_tag)
    for k,v in student_urls.items():
        student_dict[k] = v


    ## Cohort Lead
    re_cohort_lead = re.compile(r"Cohort Lead: (\w* \w*)")
    student_dict['cohort_lead'] = re_cohort_lead.findall(student_info)#[0]

    ## Ed Coach
    re_ed_coach = re.compile(r"Educational Coach: Currently assigned to (\w*.\w*)")
    student_dict['ed_coach'] = re_ed_coach.findall(student_info)#[0]


    ## Last Active
    re_last_active = re.compile(r"last.active.(\d{2,}/\d{2,}/\d{2,})")
    student_dict['last_active'] = re_last_active.findall(student_info)#[0]


    ## Completed Lessons
    re_comp_lessons = re.compile(r"(\d{1,4}).completed lessons")
    student_dict['completed_lessons'] = re_comp_lessons.findall(student_info)#[0]

    ## Joined learn
    re_joined = re.compile(r"Joined Learn (\d{2}/\d{2}/\d{2})")
    student_dict['joined'] = re_joined.findall(student_info)#[0]



    ## Career Coach - MUST BETTER ADDRESS NOT CURRENTLY ASSIGNED
    re_career_coach= re.compile(r"Career Coach: (\w* \w*)")
    student_dict['career_coach'] = re_career_coach.findall(student_info)#[0]

    re_section = re.compile(r"Section: ([A-Za-z\t .]+)")
    student_dict['section'] = re_section.findall(student_info)#[0]
    
    ## Adding Unpacking of lists via dict loop
    
    for k,v in student_dict.items():
        try:
            student_dict[k] = v[0]
        except:
            continue
        
    return student_dict




def get_program_info(program_info_tag):
    
    program_info = program_info_tag.text
    
    program_dict = {}
    
    re_coach_sess= re.compile(r"Touchpoints: (\d{1,2}) (of (\d{1,2}))?") #"Touchpoints: (\d{1,2}) of (\d{1,2})")
    num_ed_coach_sess = re_coach_sess.findall(program_info)
    
    num_used= num_ed_coach_sess[0][0]
    num_avail = num_ed_coach_sess[0][-1]
    
    program_dict['ed_coach_avail'] = num_avail
    program_dict['ed_coach_used'] = num_used

    
    re_cohort = re.compile(r"Cohort: ([A-Za-z-\d]+)")
    program_dict['cohort'] = re_cohort.findall(program_info)[0]
    
    re_pacing = re.compile(r"Pacing: ([A-Za-z-\d ]+)")
    program_dict['pacing'] =re_pacing.findall(program_info)[0]
    
    
    return program_dict
    
    

def get_profile_info(profile_info_tag):
    
    profile_dict = {}
    profile_text = profile_info_tag.text
    grad_date = re.compile(r"Ideal Graduation Date: (([\d-]?)*)")
    
    profile_dict['grad_date'] = grad_date.findall(profile_text)#[0][0]
    
    
    re_comm_level = re.compile(r"Commitment Level: (\w* Time)")
    profile_dict['commitment_level'] = re_comm_level.findall(profile_text)#[0]
    
    re_lives_in = re.compile(r"Lives in ([A-Za-z ,]+)")
    profile_dict['lives_in'] = re_lives_in.findall(profile_text)#[0]
    return profile_dict





"""tags = get_student_instruct_cards(full_url)
student_data_dict =  process_student_instruct_cards(tags)"""


def get_student_instruct_cards(driver,full_url):
    """Get the `uk-card-body` text from student's instruction.learn full url"""
    driver.get(full_url)
    my_html = driver.page_source
    student_soup = BeautifulSoup(my_html, 'html.parser')
    tags = student_soup.find_all('div',attrs={'class':'uk-card-body'})
    return tags

def process_student_instruct_cards(tags_with_cards):
    """Calls on get_student_dict_from_student_info,
    get_program_info, and get_profile_info to make
    student_data_dict.
    """
    student_info_dict = {}
    ### Tags have all 3 boxes
    # blue student_info 
    student_info = tags_with_cards[0]
    student_info_dict['student_info'] = get_student_dict_from_student_info(student_info)

    # red student_info 
    program_info = tags_with_cards[1]
    student_info_dict['program_info'] = get_program_info(program_info)

    # purple profile 
    profile_info = tags_with_cards[2]
    
    student_info_dict['profile_info'] = get_profile_info(profile_info)
    
    return student_info_dict 
    
    
def apply_student_info_retrieval(full_url):
    import time 
    time.sleep(2)
    ## Using the streamlined functions
    student_tags = get_student_instruct_cards(full_url)
    student_dict = process_student_instruct_cards(student_tags)


    student_row = pd.Series(student_dict['student_info'])
    for k,v in student_dict['program_info'].items():
        student_row[k]=v

    for k,v in student_dict['profile_info'].items():
        student_row[k]=v    

    return student_row


def load_full_student_progress(driver,learn_url):
#     driver.get(test_url)
    driver.get(learn_url)
    import time
    time.sleep(3)
    my_html = driver.page_source
    soup = BeautifulSoup(my_html, 'html.parser')
    
    soup.find('h4', class_ = 'heading heading--level-6 heading--color-green heading--font-size-larger heading--weight-bolder').text
    
    while True:
        try:
            lm = driver.find_element_by_xpath("//*[contains(text(), 'Load more')]")
            lm.click()
            time.sleep(2)
        except:
            break
    
    
    return BeautifulSoup(driver.page_source)


def get_progress_from_soup(soup):
    first_date = soup.findAll('div', 
                          class_ = 'module module--flush-wings util--padding-tl util--padding-bl')[0]
#     lessons = first_date.find('ul',
#                           class_ = 'list list--spacing-large list--separators-grey-faintest')
    
#     # lessons
#     for l_lesson in lessons.findAll('div', class_ = 'media-block__content'):
#         print(l_lesson.find('a').text)
        
    # iterate through the entire 
    all_labs = soup.findAll('div', 
                              class_ = 'module module--flush-wings util--padding-tl util--padding-bl')

    dates_list = []
    lessons_list = []

    for d in all_labs:
        date = d.find('div', 
                      class_ = 'heading heading--level-2 heading--color-grey-light').text
        lessons = d.find('ul',
                              class_ = 'list list--spacing-large list--separators-grey-faintest')
        for l_lesson in lessons.findAll('div', class_ = 'media-block__content'):
            dates_list.append(date)
            lessons_list.append(l_lesson.find('a').text)
            print(l_lesson.find('a').text)
            
            
            
    df_lessons = pd.DataFrame({'dates': dates_list,
                          'lesson': lessons_list})
    
    return df_lessons
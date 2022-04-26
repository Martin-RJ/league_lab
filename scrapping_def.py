#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from tqdm import tqdm
import time
import requests 
from bs4 import BeautifulSoup 
import re 
import os
import glob
from Library import scrapping_def as scrap


# You need : 
# - League URL ==> Choose a League and a Season then copy URL (Championship format only, no Cups or International competitions)
# - Teams URL ==> Use get_squad_links(url) with League URL
# - Team names and Team URL in a dictionary ==> Use get_team_url_dict(url) with League URL
# - Match reports URL ==> Use get_match_reports_links(team_url_dict) with get_team_url_dict(url)
# - PATHs to League Match Reports directories ==> Create it
# - PATHs to League Fixtures directories ==> Create it
# - PATHs to League Stats directories ==> Create it

# # Général

# In[2]:


#Function to get a definition of all the acronyms used in Fbref tables
def acronym_to_label(acronym):
    
    #Every acronym is put in the dictionary
    dictionary = {
                'Rk': 'Ranking',
                'Squad' : 'Squad',
                'MP' : 'Matches Played',
                'W' : 'Win',
                'D' : 'Draw',
                'L' : 'Loss',
                'GF' : 'Goals For',
                'GA' : 'Goals Against',
                'GD' : 'Goal Difference',
                'Pts' : 'Points',
                'Last 5' : 'Last 5 Matches',
                'Attendance' : 'Attendance',
                'Top Scorer' : 'Top Scorer',
                'Goals' : 'Goals',
                'MP_Home' : 'Matches Played - Home',
                'W_Home' : 'Win - Home',
                'D_Home' : 'Draw - Home',
                'L_Home' : 'Loss - Home',
                'GF_Home' : 'Goals For - Home',
                'GA_Home' : 'Goals Against - Home',
                'GD_Home': 'Goal Difference - Home',
                'Pts_Home' : 'Points - Home',
                'Pts/G_Home' : 'Points per Game - Home',
                'MP_Away': 'Matches Played - Away',
                'W_Away' : 'Win - Away',
                'D_Away' : 'Draw - Away',
                'L_Away' : 'Loss - Away',
                'GF_Away' : 'Goals For - Away',
                'GA_Away' : 'Goals Against - Away',
                'GD_Away' : 'Goal Difference - Away',
                'Pts_Away' : 'Points - Away',
                'Pts/G_Away' : 'Points per Game - Away',
                '# Pl' : 'Number of Players Used',
                'Age' : 'Age',
                'Poss' : 'Possession',
                'Starts' : 'Games Started by Player',
                'Min' : 'Minutes Played',
                'Ast' : 'Assists',
                'G-PK' : 'Non-Penalty Goals',
                'PK' : 'Penalty Kicks',
                'PKatt' : 'Penalty Kickts Attempted',
                'Ast/90' : 'Assists per 90',
                'G+A' : 'Goals and Assists per 90',
                'G+A-PK' : 'Goals and Assists minus Penalty Kicks per 90',
                'G-PK/90' : 'Non Penalty Goals per 90',
                'Compl' : 'Complete Matches Played',
                'Subs' : 'Complete Matches Played by Substitutes',
                'Mn/Sub' : 'Minutes per Substitutions',
                'unSub' : 'Complete Matches non-Played by Substitutes',
                'PPM' : 'Points per Match',
                '+/-90' : 'Goal Difference per 90',
                'Sh' : 'Total Shots',
                'SoT' : 'Shots on Target',
                'SoT%' : 'Percentage of Shots on Target',
                'Sh/90' : 'Total Shots per 90',
                'SoT/90' : 'Shots on Target per 90',
                'G/Sh' : 'Goals per Total Shots',
                'G/SoT' : 'Goals per Shots on Target',
                'GA90' : 'Goals Against per 90',
                'SoTA' : 'Shots on Target Against',
                'Saves' : 'Saves',
                'Save%' : 'Percentage of Saves',
                'CS' : 'Clean Sheets',
                'CS%' : 'Percentage of Clean Sheets',
                'PKatt against' : 'Penalty Kicks Attempted - Against',
                'PKA' : 'Penalty Kicks Scored - Against',
                'PKsv' : 'Penalty Kicks Saved - Against',
                'PKm' : 'Penalty Kicks Missed - Against',
                'PKsv%' : 'Penalty Kicks Saved Percentage - Against',
                'CrdY' : 'Yellow Cards',
                'CrdR' : 'Red Cards',
                '2CrdY' : 'Second Yellow Cards',
                'Fls' : 'Fouls Committed',
                'Fld' : 'Fouls Drawn',
                'Off' : 'Offsides',
                'Crs' : 'Crosses',
                'Int' : 'Interceptions',
                'TklW' : 'Succesful Tackles - Possession Gained',
                'OG' : 'Own Goals',
                'Player' : 'Player',
                'Nation' : 'Nation',
                'Pos' : 'Position',
                '90s' : 'Minutes Played per 90',
                'Gls' : 'Goals Scored',
                'Gls/90' : 'Goals Scored per 90',
                'G+A/90' : 'Goals and Assists per 90',
                'G+A-PK/90' : 'Goals and Assists minus Penalty Kicks per 90',
                'Mn/MP' : 'Minutes per Match Played',
                'Min%' : 'Percentage of Minutes Played',
                'Mn/Start' : 'Minutes per Match Started',
                'onG' : 'Goals Scored by Team while on Pitch',
                'onGA' : 'Goals Conceded by Team while on Pitch',
                '+/-' : 'Goal Difference while on Pitch',
                'On-Off' : ' Net Goal Difference while on Pitch',
                'PKatt-GK' : 'Penalty Kicks Attempted - Against'
                  }
    #and then returned when the function is called
    return dictionary[acronym]
    


# In[3]:


#Function to get links for teams
#Need League URL
#Works only for Championship formats (no Cups : national, continental or worldwide)
def get_squad_links(url):
    
    #Empty list that will be appended with results and returned
    data = []
    
    #"for loop" scraping team url links
    page = requests.get(url) 
    soup = BeautifulSoup(page.content, 'html.parser') 
    for table in soup.find_all('table', id="stats_squads_standard_against"):
        for tr in table.find_all('tr'):
            for a in tr.find_all('a'):
                data.append(a['href'])
   
    #Complete the url format and select only teams in the list
    df_data = pd.DataFrame(data)
    df_data[0] = 'https://fbref.com' + df_data[0].astype(str)
    contain_values = df_data[df_data[0].str.contains('squads')]
    squad_links = contain_values.values.tolist()
    
    return squad_links


# In[4]:


#Function to get a dictionary of Teams and related URLs
#Need League URL
def get_team_url_dict(url):
    
    #Create empty lists and call get_squad_links function with the League URL
    link = get_squad_links(url)
    urls = []
    team_names = []
    
    #Get URl for every team in the League
    for teams in link :
        url = ",".join(teams)
        urls.append(url)
        
    #Get team names for every team in the League
    for teams in link :
        url = ",".join(teams)
        team_name = url.split('/')[6]
        team_name = team_name.split('-')[:-1]
        team_name = " ".join(team_name)
        team_names.append(team_name)

    #Zip both lists into a dictionary
    team_url = dict(zip(team_names, urls))
    
    return team_url


# In[5]:


#Function to get the last Gameweek played in a League
#Need League URL
def get_last_gameweek(url):
    
    #Get the current ranking and assign to last gameweek the highest number of Match Played in the league
    df = scrap.get_overall_league_table(url)
    gameweek = df['MP'].max()
    
    return gameweek


# # League One et League Two

# Fonction pour obtenir un df du classement de la Ligue

# In[6]:


#Function to get a dataframe of the League table
#Need the url of the League
def get_overall_league_table(url):
    
    #As of April 2022, League table is table[0]
    overall_league_table = pd.read_html(url)[0]
 
    return overall_league_table


# Fonction pour obtenir un df du classement Home/Away de la Ligue

# In[7]:


#Function to get a dataframe of the Home/Away table
#Need the url of the League
def get_homeaway_league_table(url):
    
    #As of April 2022, Home/Away table is table[1]
    homeaway_league_table = pd.read_html(url)[1]
 
    return homeaway_league_table


# Fonction pour obtenir un df des Squad Standard Stats

# In[8]:


#Function to get a dataframe of the Squad Standard Stats table
#Need the url of the League
def get_squad_stats(url):
    
    #As of April 2022, Squad Standard Stats table is table[2]
    squad_stats = pd.read_html(url)[2]
 
    return squad_stats


# Fonction pour obtenir un df des Opp Standard Stats

# In[9]:


#Function to get a dataframe of the Opposition Standard Stats table
#Need the url of the League
def get_opp_stats(url):
    
    #As of April 2022, Opposition Standard Stats table is table[3]
    opp_stats = pd.read_html(url)[3]
 
    return opp_stats


# Fonction pour obtenir un df des Goalkeeping Stats

# In[10]:


#Function to get a dataframe of the Goalkeeping Stats table
#Need the url of the League
def get_gk_stats(url):
    
    #As of April 2022, Goalkeeping Stats table is table[4]
    gk_stats = pd.read_html(url)[4]
 
    return gk_stats


# Fonction pour obtenir un df des Opp Goalkeeping Stats

# In[11]:


#Function to get a dataframe of the Opposition Goalkeeping Stats table
#Need the url of the League
def get_opp_gk_stats(url):
    
    #As of April 2022, Opposition Goalkeeping Stats table is table[5]
    opp_gk_stats = pd.read_html(url)[5]
 
    return opp_gk_stats


# Fonction pour obtenir un df des Shooting stats

# In[12]:


#Function to get a dataframe of the Shooting Stats table
#Need the url of the League
def get_shoot_stats(url):
    
    #As of April 2022, Shooting Stats table is table[6]
    shoot_stats = pd.read_html(url)[6]
 
    return shoot_stats


# Fonction pour obtenir un df des Opp Shooting Stats

# In[13]:


#Function to get a dataframe of the Opposition Shooting Stats table
#Need the url of the League
def get_opp_shoot_stats(url):
    
    #As of April 2022, Opposition Shooting Stats table is table[7]
    opp_shoot_stats = pd.read_html(url)[7]
 
    return opp_shoot_stats


# Fonction pour obtenir un df des Playing Times

# In[14]:


#Function to get a dataframe of the Playing Times table
#Need the url of the League
def get_play_time(url):
    
    #As of April 2022, Playing Times table is table[8]
    play_time = pd.read_html(url)[8]
 
    return play_time


# Fonction pour obtenir un df des Opp Playing Times

# In[15]:


#Function to get a dataframe of the Opposition Playing Times table
#Need the url of the League
def get_opp_play_time(url):
    
    #As of April 2022, Opposition Playing Times table is table[9]
    opp_play_time = pd.read_html(url)[9]
 
    return opp_play_time


# Fonction pour obtenir un df des Miscellaneous Stats

# In[16]:


#Function to get a dataframe of the Miscellaneous Stats table
#Need the url of the League
def get_misc_stats(url):
    
    #As of April 2022, Miscellaneous Stats table is table[10]
    misc_stats = pd.read_html(url)[10]
 
    return misc_stats


# Fonction pour obtenir un df des Opp Miscellaneous Stats

# In[17]:


#Function to get a dataframe of the Opposition Miscellaneous Stats table
#Need the url of the League
def get_opp_misc_stats(url):
    
    #As of April 2022, Opposition Miscellaneous Stats table is table[11]
    opp_misc_stats = pd.read_html(url)[11]
 
    return opp_misc_stats


# # Teams en League One et League Two

# Fonction pour obtenir un df des Standard Stats

# In[18]:


#Function to get a dataframe of the Team Standard Stats table
#Need the url of the Team
def get_team_std_stats(url):
    
    #As of April 2022, Team Standard Stats table is table[0]
    std_stats = pd.read_html(url)[0]
 
    return std_stats


# Fonction pour obtenir un df des Score et Fixtures Stats

# In[19]:


#Function to get a dataframe of the Team Score Stats table
#Need the url of the Team
def get_team_score_stats(url):
    
    #As of April 2022, Team Score Stats table is table[1]
    score_stats = pd.read_html(url)[1]
 
    return score_stats


# Fonction pour obtenir un df des Goalkeeping Stats

# In[20]:


#Function to get a dataframe of the Team Goalkeeping Stats table
#Need the url of the Team
def get_team_gk_stats(url):
    
    #As of April 2022, Team Goalkeeping Stats table is table[2]
    gk_stats = pd.read_html(url)[2]
 
    return gk_stats


# Fonction pour obtenir un df des Shooting Stats

# In[21]:


#Function to get a dataframe of the Team Shooting Stats table
#Need the url of the Team
def get_team_shoot_stats(url):
   
    #As of April 2022, Team Shooting Stats table is table[3]
    shoot_stats = pd.read_html(url)[3]
 
    return shoot_stats


# Fonction pour obtenir un df des Playing Times

# In[22]:


#Function to get a dataframe of the Team Playing Times table
#Need the url of the Team
def get_team_play_time(url):
    
    #As of April 2022, Team Playing Times table is table[4]
    play_time = pd.read_html(url)[4]
 
    return play_time


# Fonction pour obtenir un df des Miscellaneous Stats

# In[23]:


#Function to get a dataframe of the Team Miscellaneous Stats table
#Need the url of the Team
def get_team_misc_stats(url):
    
    #As of April 2022, Team Miscellaneous Stats table is table[5]
    misc_stats = pd.read_html(url)[5]
 
    return misc_stats


# # Obtenir les match reports

# In[24]:


#Function to get links for match reports
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_match_reports_links(team_url_dict):
    
    #Empty list that will be appended with results and returned
    link = []
   
    #"for loop" scraping match reports links
    for teams, url in team_url_dict.items() :
        page = requests.get(url) 
        soup = BeautifulSoup(page.content, 'html.parser') 
        extract = soup.find_all('a', text='Match Report') 
        for item in extract: 
            href = item.get('href')
            long_href = f'https://fbref.com{href}'
            link.insert(len(link), long_href)
            df_link = pd.DataFrame(link)

    #Drop duplicates from DataFrame and remove Cup games, then transform into List
    df_link = df_link.drop_duplicates()
    df_link = df_link.rename(columns={0: "Lien"})
    df_link = df_link[~df_link.Lien.str.contains("Cup")]
    link_list = df_link['Lien'].values.tolist()
    return link_list


# In[25]:


#Function to get the Player Stats table for the Home Team from a match report
#Need match report url
def get_match_report_teamA_player_stats_table(url):
    
    #Depending on the layout of the page, the table we want can have a different index
    if len(pd.read_html(url)) == 7 : 
        match_report_teamA_player_stats = pd.read_html(url)[3]
    elif len(pd.read_html(url)) == 6 :
        match_report_teamA_player_stats = pd.read_html(url)[2]
    elif len(pd.read_html(url)) == 5 :
        match_report_teamA_player_stats = pd.read_html(url)[1]
    elif len(pd.read_html(url)) == 4 :
        match_report_teamA_player_stats = pd.read_html(url)[0]
 
    return match_report_teamA_player_stats


# In[26]:


#Function to get the Goalkeeper Stats table for the Home Team from a match report
#Need match report url
def get_match_report_teamA_gk_stats_table(url):
    
    #Depending on the layout of the page, the table we want can have a different index
    if len(pd.read_html(url)) == 7 : 
        match_report_teamA_gk_stats = pd.read_html(url)[4]
    elif len(pd.read_html(url)) == 6 :
        match_report_teamA_gk_stats = pd.read_html(url)[3]
    elif len(pd.read_html(url)) == 5 :
        match_report_teamA_gk_stats = pd.read_html(url)[2]
    elif len(pd.read_html(url)) == 4 :
        match_report_teamA_gk_stats = pd.read_html(url)[1]
 
    return match_report_teamA_gk_stats


# In[27]:


#Function to get the Player Stats table for the Away Team from a match report
#Need match report url
def get_match_report_teamB_player_stats_table(url):
    
    #Depending on the layout of the page, the table we want can have a different index
    if len(pd.read_html(url)) == 7 : 
        match_report_teamB_player_stats = pd.read_html(url)[5]
    elif len(pd.read_html(url)) == 6 :
        match_report_teamB_player_stats = pd.read_html(url)[4]
    elif len(pd.read_html(url)) == 5 :
        match_report_teamB_player_stats = pd.read_html(url)[3]
    elif len(pd.read_html(url)) == 4 :
        match_report_teamB_player_stats = pd.read_html(url)[2]
 
    return match_report_teamB_player_stats


# In[28]:


#Function to get the Goalkeeper Stats table for the Away Team from a match report
#Need match report url
def get_match_report_teamB_gk_stats_table(url):
    
    #Depending on the layout of the page, the table we want can have a different index
    if len(pd.read_html(url)) == 7 : 
        match_report_teamB_gk_stats = pd.read_html(url)[6]
    elif len(pd.read_html(url)) == 6 :
        match_report_teamB_gk_stats = pd.read_html(url)[5]
    elif len(pd.read_html(url)) == 5 :
        match_report_teamB_gk_stats = pd.read_html(url)[4]
    elif len(pd.read_html(url)) == 4 :
        match_report_teamB_gk_stats = pd.read_html(url)[3]
 
    return match_report_teamB_gk_stats


# In[29]:


#Function to get one concatenated dataframe of all the available and clean League One match reports
#Need PATH to League One Match Reports directory
def get_concatenated_l1_match_reports(PATH) :
    
    #get all the csv files in the League One Match Reports directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)

    #print out to a new csv file
    result.to_csv(fr"{PATH}\League_One_Concatenated_Match_Reports.csv",index = False)


# In[30]:


#Function to get one concatenated dataframe of all the available and clean League Two match reports
#Need PATH to League Two Match Reports directory
def get_concatenated_l2_match_reports(PATH) :
    
    #get all the csv files in the League Two Match Reports directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)

    #print out to a new csv file
    result.to_csv(fr"{PATH}\League_Two_Concatenated_Match_Reports.csv",index = False)


# In[31]:


#Function to get all the data from match reports in a single csv file per game
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l1_match_reports_data(PATH, team_url_dict) :
    
    #Get all the match report links for a given league
    linklist = scrap.get_match_reports_links(team_url_dict)
    
    #Get the fixtures yearly calendar for League One and League Two
    df_fixture_l1 = pd.read_csv(fr"{PATH}\England-League-One-fixture-2021-2022.csv", header=None)

    #Create a dataframe of all the fixtures of League One and add a column with the corresponding match
    df_fixture_l1[['Gameweek','Club', 'Opponent']] = df_fixture_l1[0].str.split(';',expand=True)
    df_fixture_l1 = df_fixture_l1[['Gameweek','Club', 'Opponent']]
    df_fixture_l1['Match'] = df_fixture_l1['Club'] + '-' + df_fixture_l1['Opponent']

    #Iterate on every team and every url provided
    for url in linklist :

        #Get the Player Stats for the Home Team
        #Clean the data
        #Remove unnecessary data
        df_squad_a = scrap.get_match_report_teamA_player_stats_table(url)
        df_squad_a.columns = df_squad_a.columns.droplevel()
        df_squad_a.drop(df_squad_a.index[-1:], inplace=True)
        df_squad_a[['Drapeau','Nation']] = df_squad_a["Nation"].str.split(" ", 1, expand=True)
        df_squad_a[['Age','Jours']] = df_squad_a["Age"].str.split("-", 1, expand=True)
        if df_squad_a['Pos'].str.contains(',').any():
            df_squad_a[['Pos','Pos2']] = df_squad_a["Pos"].str.split(",", 1, expand=True)
            df_squad_a.drop(['Pos2'], axis=1, inplace=True)
        df_squad_a.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_squad_a = df_squad_a.fillna(0)
        df_squad_a.rename(columns={"#": "Number"}, inplace=True)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_squad_a['Club'] = scrap.get_club_home(url)
        first_column = df_squad_a.pop('Club')
        df_squad_a.insert(0, 'Club', first_column)
        df_squad_a['Opponent'] = scrap.get_club_away(url)
        first_column = df_squad_a.pop('Opponent')
        df_squad_a.insert(1, 'Opponent', first_column)

        #Get the Goalkeeper Stats for the Home Team
        #Clean the data
        #Remove unnecessary data
        df_gk_a = scrap.get_match_report_teamA_gk_stats_table(url)
        df_gk_a.columns = df_gk_a.columns.droplevel()
        df_gk_a[['Drapeau','Nation']] = df_gk_a["Nation"].str.split(" ", 1, expand=True)
        df_gk_a[['Age','Jours']] = df_gk_a["Age"].str.split("-", 1, expand=True)
        df_gk_a.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk_a = df_gk_a.fillna(0)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_gk_a['Club'] = scrap.get_club_home(url)
        first_column = df_gk_a.pop('Club')
        df_gk_a.insert(0, 'Club', first_column)
        df_gk_a['Opponent'] = scrap.get_club_away(url)
        first_column = df_gk_a.pop('Opponent')
        df_gk_a.insert(1, 'Opponent', first_column)

        #Get the Goalkeeper Stats for the Away Team
        #Clean the data
        #Remove unnecessary data
        df_gk_b = scrap.get_match_report_teamB_gk_stats_table(url)
        df_gk_b.columns = df_gk_b.columns.droplevel()
        df_gk_b[['Drapeau','Nation']] = df_gk_b["Nation"].str.split(" ", 1, expand=True)
        df_gk_b[['Age','Jours']] = df_gk_b["Age"].str.split("-", 1, expand=True)
        df_gk_b.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk_b = df_gk_b.fillna(0)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_gk_b['Club'] = scrap.get_club_away(url)
        first_column = df_gk_b.pop('Club')
        df_gk_b.insert(0, 'Club', first_column)
        df_gk_b['Opponent'] = scrap.get_club_home(url)
        first_column = df_gk_b.pop('Opponent')
        df_gk_b.insert(1, 'Opponent', first_column)

        #Get the Player Stats for the Away Team
        #Clean the data
        #Remove unnecessary data
        df_squad_b = scrap.get_match_report_teamB_player_stats_table(url)
        df_squad_b.columns = df_squad_b.columns.droplevel()
        df_squad_b.drop(df_squad_b.index[-1:], inplace=True)
        df_squad_b[['Drapeau','Nation']] = df_squad_b["Nation"].str.split(" ", 1, expand=True)
        df_squad_b[['Age','Jours']] = df_squad_b["Age"].str.split("-", 1, expand=True)
        if df_squad_b['Pos'].str.contains(',').any():
            df_squad_b[['Pos','Pos2']] = df_squad_b["Pos"].str.split(",", 1, expand=True)
            df_squad_b.drop(['Pos2'], axis=1, inplace=True)
        df_squad_b.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_squad_b = df_squad_b.fillna(0)
        df_squad_b.rename(columns={"#": "Number"}, inplace=True)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_squad_b['Club'] = scrap.get_club_away(url)
        first_column = df_squad_b.pop('Club')
        df_squad_b.insert(0, 'Club', first_column)
        df_squad_b['Opponent'] = scrap.get_club_home(url)
        first_column = df_squad_b.pop('Opponent')
        df_squad_b.insert(1, 'Opponent', first_column)

        #Merge Player and Goalkeeper Stats for the Home team
        #Merge this new dataframe with the fixture calendar
        df_home = pd.merge(df_squad_a,df_gk_a[{'Player', 'SoTA', 'GA', 'Saves', 'Save%'}], on='Player', how='left').fillna(0)
        df_home = pd.merge(df_home,df_fixture_l1, on=['Club', 'Opponent'], how='left')

        #Merge Player and Goalkeeper Stats for the Home team
        df_away = pd.merge(df_squad_b,df_gk_b[{'Player', 'SoTA', 'GA', 'Saves', 'Save%'}], on='Player', how='left').fillna(0)

        #Concatenate the data for Home and Away teams as well as fixture schedule
        df_match = pd.concat([df_home, df_away], ignore_index=True)
        df_match['Gameweek'] = df_match['Gameweek'].fillna(df_match['Gameweek'][0])
        df_match['Match'] = df_match['Match'].fillna(df_match['Match'][0])
        cols = list(df_match.columns.values)
        cols.pop(cols.index('Match'))
        cols.pop(cols.index('Gameweek'))
        df_match = df_match[['Gameweek','Match']+cols]
        
        #Create variables to call later to name the csv file
        match = df_match['Match'][0]
        gameweek = df_match['Gameweek'][0]

        #Return CSV containing all the data for a given game in the league
        df_match.to_csv(fr"{PATH}\Gameweek {gameweek}_{match}_Match Report.csv",index = False)


# In[32]:


#Function to get all the data from match reports in a single csv file per game
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l2_match_reports_data(PATH, team_url_dict) :
    
    #Get all the match report links for a given league
    linklist = scrap.get_match_reports_links(team_url_dict)
    
    #Get the fixtures yearly calendar for League One and League Two
    df_fixture_l2 = pd.read_csv(fr"{PATH}\England-League-Two-fixture-2021-2022.csv", header=None)

    #Create a dataframe of all the fixtures of League Two and add a column with the corresponding match
    df_fixture_l2[['Gameweek','Club', 'Opponent']] = df_fixture_l2[0].str.split(';',expand=True)
    df_fixture_l2 = df_fixture_l2[['Gameweek','Club', 'Opponent']]
    df_fixture_l2['Match'] = df_fixture_l2['Club'] + '-' + df_fixture_l2['Opponent']
        
    #Iterate on every team and every url provided
    for url in linklist :

        #Get the Player Stats for the Home Team
        #Clean the data
        #Remove unnecessary data
        df_squad_a = scrap.get_match_report_teamA_player_stats_table(url)
        df_squad_a.columns = df_squad_a.columns.droplevel()
        df_squad_a.drop(df_squad_a.index[-1:], inplace=True)
        df_squad_a[['Drapeau','Nation']] = df_squad_a["Nation"].str.split(" ", 1, expand=True)
        df_squad_a[['Age','Jours']] = df_squad_a["Age"].str.split("-", 1, expand=True)
        if df_squad_a['Pos'].str.contains(',').any():
            df_squad_a[['Pos','Pos2']] = df_squad_a["Pos"].str.split(",", 1, expand=True)
            df_squad_a.drop(['Pos2'], axis=1, inplace=True)
        df_squad_a.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_squad_a = df_squad_a.fillna(0)
        df_squad_a.rename(columns={"#": "Number"}, inplace=True)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_squad_a['Club'] = scrap.get_club_home(url)
        first_column = df_squad_a.pop('Club')
        df_squad_a.insert(0, 'Club', first_column)
        df_squad_a['Opponent'] = scrap.get_club_away(url)
        first_column = df_squad_a.pop('Opponent')
        df_squad_a.insert(1, 'Opponent', first_column)

        #Get the Goalkeeper Stats for the Home Team
        #Clean the data
        #Remove unnecessary data
        df_gk_a = scrap.get_match_report_teamA_gk_stats_table(url)
        df_gk_a.columns = df_gk_a.columns.droplevel()
        df_gk_a[['Drapeau','Nation']] = df_gk_a["Nation"].str.split(" ", 1, expand=True)
        df_gk_a[['Age','Jours']] = df_gk_a["Age"].str.split("-", 1, expand=True)
        df_gk_a.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk_a = df_gk_a.fillna(0)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_gk_a['Club'] = scrap.get_club_home(url)
        first_column = df_gk_a.pop('Club')
        df_gk_a.insert(0, 'Club', first_column)
        df_gk_a['Opponent'] = scrap.get_club_away(url)
        first_column = df_gk_a.pop('Opponent')
        df_gk_a.insert(1, 'Opponent', first_column)

        #Get the Goalkeeper Stats for the Away Team
        #Clean the data
        #Remove unnecessary data
        df_gk_b = scrap.get_match_report_teamB_gk_stats_table(url)
        df_gk_b.columns = df_gk_b.columns.droplevel()
        df_gk_b[['Drapeau','Nation']] = df_gk_b["Nation"].str.split(" ", 1, expand=True)
        df_gk_b[['Age','Jours']] = df_gk_b["Age"].str.split("-", 1, expand=True)
        df_gk_b.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk_b = df_gk_b.fillna(0)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_gk_b['Club'] = scrap.get_club_away(url)
        first_column = df_gk_b.pop('Club')
        df_gk_b.insert(0, 'Club', first_column)
        df_gk_b['Opponent'] = scrap.get_club_home(url)
        first_column = df_gk_b.pop('Opponent')
        df_gk_b.insert(1, 'Opponent', first_column)

        #Get the Player Stats for the Away Team
        #Clean the data
        #Remove unnecessary data
        df_squad_b = scrap.get_match_report_teamB_player_stats_table(url)
        df_squad_b.columns = df_squad_b.columns.droplevel()
        df_squad_b.drop(df_squad_b.index[-1:], inplace=True)
        df_squad_b[['Drapeau','Nation']] = df_squad_b["Nation"].str.split(" ", 1, expand=True)
        df_squad_b[['Age','Jours']] = df_squad_b["Age"].str.split("-", 1, expand=True)
        if df_squad_b['Pos'].str.contains(',').any():
            df_squad_b[['Pos','Pos2']] = df_squad_b["Pos"].str.split(",", 1, expand=True)
            df_squad_b.drop(['Pos2'], axis=1, inplace=True)
        df_squad_b.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_squad_b = df_squad_b.fillna(0)
        df_squad_b.rename(columns={"#": "Number"}, inplace=True)

        #Add a 'Club' and 'Opponent' column to the table to be able to merge later on
        df_squad_b['Club'] = scrap.get_club_away(url)
        first_column = df_squad_b.pop('Club')
        df_squad_b.insert(0, 'Club', first_column)
        df_squad_b['Opponent'] = scrap.get_club_home(url)
        first_column = df_squad_b.pop('Opponent')
        df_squad_b.insert(1, 'Opponent', first_column)

        #Merge Player and Goalkeeper Stats for the Home team
        #Merge this new dataframe with the fixture calendar
        df_home = pd.merge(df_squad_a,df_gk_a[{'Player', 'SoTA', 'GA', 'Saves', 'Save%'}], on='Player', how='left').fillna(0)
        df_home = pd.merge(df_home,df_fixture_l2, on=['Club', 'Opponent'], how='left')

        #Merge Player and Goalkeeper Stats for the Home team
        df_away = pd.merge(df_squad_b,df_gk_b[{'Player', 'SoTA', 'GA', 'Saves', 'Save%'}], on='Player', how='left').fillna(0)

        #Concatenate the data for Home and Away teams as well as fixture schedule
        df_match = pd.concat([df_home, df_away], ignore_index=True)
        df_match['Gameweek'] = df_match['Gameweek'].fillna(df_match['Gameweek'][0])
        df_match['Match'] = df_match['Match'].fillna(df_match['Match'][0])
        cols = list(df_match.columns.values)
        cols.pop(cols.index('Match'))
        cols.pop(cols.index('Gameweek'))
        df_match = df_match[['Gameweek','Match']+cols]
        
        #Create variables to call later to name the csv file
        match = df_match['Match'][0]
        gameweek = df_match['Gameweek'][0]

        #Return CSV containing all the data for a given game in the league
        df_match.to_csv(fr"{PATH}\Gameweek {gameweek}_{match}_Match Report.csv",index = False)


# # Obtenir les Fixtures de League One

# In[33]:


#Function to get League One fixtures
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l1teams_fixtures(PATH, team_url_dict):
    
    #Iterate on every team and every url provided
    for teams, url in team_url_dict.items() :         
    
        #Scrape fixtures calendar using a predefined function. 
        #Drop Match reports and Notes columns. 
        #Drop and non League game
        #Set GF and GA to integer
        #Set time as Datetime 
        df_score = scrap.get_team_score_stats(url)
        df_score.drop(['Match Report', 'Notes'], axis=1, inplace=True)
        df_score = df_score[df_score['Comp'] == 'League One']
        df_score[['GF', 'GA']] = df_score[['GF', 'GA']].fillna(0).astype(int)
        df_score['Date'] = pd.to_datetime(df_score['Date'], format='%Y-%m-%d')
        df_score['Time'] = pd.to_datetime(df_score['Time'], format='%H:%M')
        df_score['Time'] = df_score['Time'].dt.time
        
        #Add club to the data
        df_score['Club'] = f"{teams}"
        new_column = df_score.pop('Club')
        df_score.insert(9, 'Club', new_column)
        
        #Rename 'Opponent' to match 'Club'
        df_score.loc[df_score["Opponent"] == "Cambridge Utd", 'Opponent'] = 'Cambridge United'
        df_score.loc[df_score["Opponent"] == "MK Dons", 'Opponent'] = 'Milton Keynes Dons'
        df_score.loc[df_score["Opponent"] == "Shrewsbury", 'Opponent'] = 'Shrewsbury Town'
        df_score.loc[df_score["Opponent"] == "Acc'ton Stanley", 'Opponent'] = 'Accrington Stanley'
        df_score.loc[df_score["Opponent"] == "Cheltenham", 'Opponent'] = 'Cheltenham United'
        df_score.loc[df_score["Opponent"] == "Charlton Ath", 'Opponent'] = 'Charlton Athletic'
        df_score.loc[df_score["Opponent"] == "Sheffield Weds", 'Opponent'] = 'Sheffield Wednesday'
        df_score.loc[df_score["Opponent"] == "Bolton", 'Opponent'] = 'Bolton Wanderers'
        df_score.loc[df_score["Opponent"] == "Rotherham Utd", 'Opponent'] = 'Rotherham United'
        df_score.loc[df_score["Opponent"] == "Doncaster", 'Opponent'] = 'Doncaster Rovers'
        df_score.loc[df_score["Opponent"] == "Wycombe", "Opponent"] = 'Wycombe Wanderers'
    
        #Return CSV containing fixtures for every single League One teams and url provided
        df_score.to_csv(fr"{PATH}\\{teams}_League_One_fixtures.csv",index = True)


# In[34]:


#Function to get one concatenated dataframe of all the available and clean League One fixtures
#Need PATH to League One Fixtures directory
def get_concatenated_l1_fixtures(PATH):
    
    #get all the csv files in the League One Fixtures directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)

    #print out to a new csv file
    result.to_csv(fr"{PATH}\League_One_Concatenated_Fixtures.csv",index = False)


# # Obtenir les fixtures de League Two

# In[35]:


#Function to get League Two fixtures
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l2teams_fixtures(PATH, team_url_dict):
    
    #Iterates on every team and every url provided
    for teams, url in team_url_dict.items() :         
    
        #Scrapes fixtures calendar using a predefined function. 
        #Drops Match reports and Notes columns. 
        #Drops and non League game
        #Sets GF and GA to integer
        #Sets time as Datetime 
        df_score = scrap.get_team_score_stats(url)
        df_score.drop(['Match Report', 'Notes'], axis=1, inplace=True)
        df_score = df_score[df_score['Comp'] == 'League One']
        df_score[['GF', 'GA']] = df_score[['GF', 'GA']].fillna(0).astype(int)
        df_score['Date'] = pd.to_datetime(df_score['Date'], format='%Y-%m-%d')
        df_score['Time'] = pd.to_datetime(df_score['Time'], format='%H:%M')
        df_score['Time'] = df_score['Time'].dt.time
        
        #Add club to the data
        df_score['Club'] = f"{teams}"
        new_column = df_score.pop('Club')
        df_score.insert(9, 'Club', new_column)
        
        #Rename 'Opponent' to match 'Club'
        df_score.loc[df_score["Opponent"] == "Hartlepool Utd", 'Opponent'] = 'Hartlepool United'
        df_score.loc[df_score["Opponent"] == "Harrogate", 'Opponent'] = 'Harrogate Town'
        df_score.loc[df_score["Opponent"] == "Colchester Utd", 'Opponent'] = 'Colchester United'
        df_score.loc[df_score["Opponent"] == "Scunthorpe Utd", 'Opponent'] = 'Scunthorpe United'
        df_score.loc[df_score["Opponent"] == "FG Rovers", 'Opponent'] = 'Forest Green Rovers'
        df_score.loc[df_score["Opponent"] == "Northampton", 'Opponent'] = 'Northampton Town'
    
        #Returns CSV containing fixtures for every single League Two teams and url provided
        df_score.to_csv(fr"{PATH}\\{teams}_League_Two_fixtures.csv",index = True)


# In[36]:


#Function to get one concatenated dataframe of all the available and clean League Two fixtures
#Need PATH to League One Fixtures directory
def get_concatenated_l2_fixtures(PATH):
    
    #get all the csv files in the League Two Fixtures directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)

    #print out to a new csv file
    result.to_csv(fr"{PATH}\League_Two_Concatenated_Fixtures.csv",index = False)


# # Obtenir les Stats de League One

# In[37]:


#Function to get League One stats
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l1teams_stats(team_url_dict, PATH):
    
    #Iterate on every team and every url provided
    for teams, url in team_url_dict.items() : 
        
        #Scrape team stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Rename columns to avoid duplicated names
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        df_squad = scrap.get_team_std_stats(url)
        df_squad.columns = df_squad.columns.droplevel()
        df_squad.drop(df_squad.index[-2:], inplace=True)
        df_squad.drop('Matches', axis=1, inplace=True)
        df_squad[['Drapeau','Nation']] = df_squad["Nation"].str.split(" ", 1, expand=True)
        df_squad[['Age','Jours']] = df_squad["Age"].str.split("-", 1, expand=True)
        df_squad[['Pos','Pos2']] = df_squad["Pos"].str.split(",", 1, expand=True)
        df_squad.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_squad.columns.values[15] = 'Gls/90'
        df_squad.columns.values[16] = 'Ast/90'
        df_squad.columns.values[17] = 'G+A/90'
        df_squad.columns.values[18] = 'G-PK/90'
        df_squad.columns.values[19] = 'G+A-PK/90'
        df_squad = df_squad[df_squad['Min'].notna()].fillna(0)

        #Scrape goalkeeper stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation and age.
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_gk = scrap.get_team_gk_stats(url)
        df_gk.columns = df_gk.columns.droplevel()
        df_gk.drop(df_gk.index[-2:], inplace=True)
        df_gk.drop('Matches', axis=1, inplace=True)
        df_gk[['Drapeau','Nation']] = df_gk["Nation"].str.split(" ", 1, expand=True)
        df_gk[['Age','Jours']] = df_gk["Age"].str.split("-", 1, expand=True)
        df_gk.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk = df_gk[df_gk['Min'].notna()].fillna(0)
        df_gk.columns.values[18] = 'PKatt-GK'
        df_gk.columns.values[22] = 'PKsv%'
        df_gk.drop(['Nation', 'Pos', 'Age', 'MP', 'Starts', 'Min', '90s'], inplace=True, axis=1)

        #Scrape shooting stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_shoot = scrap.get_team_shoot_stats(url)
        df_shoot.columns = df_shoot.columns.droplevel()
        df_shoot.drop(df_shoot.index[-2:], inplace=True)
        df_shoot.drop(['Matches', 'Dist'], axis=1, inplace=True)
        df_shoot[['Drapeau','Nation']] = df_shoot["Nation"].str.split(" ", 1, expand=True)
        df_shoot[['Age','Jours']] = df_shoot["Age"].str.split("-", 1, expand=True)
        df_shoot[['Pos','Pos2']] = df_shoot["Pos"].str.split(",", 1, expand=True)
        df_shoot.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_shoot = df_shoot[df_shoot['90s'].notna()].fillna(0)
        df_shoot.drop(['Nation', 'Pos', 'Age', '90s', 'Gls', 'PK', 'PKatt'], inplace=True, axis=1)

        #Scrape playing time stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_play = scrap.get_team_play_time(url)
        df_play.columns = df_play.columns.droplevel()
        df_play.drop(df_play.index[-2:], inplace=True)
        df_play.drop('Matches', axis=1, inplace=True)
        df_play[['Drapeau','Nation']] = df_play["Nation"].str.split(" ", 1, expand=True)
        df_play[['Age','Jours']] = df_play["Age"].str.split("-", 1, expand=True)
        df_play[['Pos','Pos2']] = df_play["Pos"].str.split(",", 1, expand=True)
        df_play.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_play = df_play[df_play['Min'].notna()].fillna(0)
        df_play.drop(['Nation', 'Pos', 'Age', 'MP', 'Starts', 'Min', '90s'], inplace=True, axis=1)

        #Scrape miscellaneous stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_misc = scrap.get_team_misc_stats(url)
        df_misc.columns = df_misc.columns.droplevel()
        df_misc.drop(df_misc.index[-2:], inplace=True)
        df_misc.drop(['Matches', 'PKwon', 'PKcon'], axis=1, inplace=True)
        df_misc[['Drapeau','Nation']] = df_misc["Nation"].str.split(" ", 1, expand=True)
        df_misc[['Age','Jours']] = df_misc["Age"].str.split("-", 1, expand=True)
        df_misc[['Pos','Pos2']] = df_misc["Pos"].str.split(",", 1, expand=True)
        df_misc.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_misc = df_misc[df_misc['90s'].notna()].fillna(0)
        df_misc.drop(['Nation', 'Pos', 'Age', '90s', 'CrdY', 'CrdR'], inplace=True, axis=1)

        #Merge DataFrames into a main one
        merge1 = pd.merge(df_squad, df_play, how='left', on=['Player'])
        merge2 = pd.merge(merge1, df_shoot, how='left', on=['Player'])
        merge3 = pd.merge(merge2, df_misc, how='left', on=['Player'])
        df_team = pd.merge(merge3, df_gk, how='left', on=['Player'])

        #Add a Club column based on the Teams name provided.
        #Put it as the 1st column
        df_team['Club'] = f"{teams}"
        first_column = df_team.pop('Club')
        df_team.insert(0, 'Club', first_column)
        
        #Return CSV containing stats for every single League One teams and url provided
        df_team.to_csv(fr"{PATH}\League_One_{teams}_stats.csv",index = True)


# In[38]:


#Function to concatenate the League stats per gameweek
#Need a PATH to the League Stats directory and the URL of the League
def get_concatenated_l1_stats(PATH, url):
    
    #Get all the csv files in the directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)
    
    #Add a Gameweek column
    result['End of Gameweek'] = scrap.get_last_gameweek(url)
    first_column = result.pop('End of Gameweek')
    result.insert(0, 'End of Gameweek', first_column)
    gameweek = result['End of Gameweek'][0]

    #print out to a new csv file
    result.to_csv(fr"{PATH}\Stats per GW\League_One_Concatenated_Stats_GW{gameweek}.csv",index = False)


# In[39]:


#Function to get a concatenated file of all the League stats per gameweek
#Need a PATH to the concatenated League stats per gameweek
def global_l1_stats(PATH) :
    
    #Get all the csv files in the directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)
    
    #print out to a new csv file
    result.to_csv(fr"{PATH}\Global L1 Stats\Global_League_One_Stats.csv",index = False)


# # Obtenir les Stats de League Two

# In[40]:


#Function to get League Two stats
#Need team name and team url in a dict ==> ({'Team' : 'url'})
def get_l2teams_stats(team_url_dict, PATH):
    
    #Iterates on every team and every url provided
    for teams, url in team_url_dict.items() : 
        
        #Scrape team stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Rename columns to avoid duplicated names
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        df_squad = scrap.get_team_std_stats(url)
        df_squad.columns = df_squad.columns.droplevel()
        df_squad.drop(df_squad.index[-2:], inplace=True)
        df_squad.drop('Matches', axis=1, inplace=True)
        df_squad[['Drapeau','Nation']] = df_squad["Nation"].str.split(" ", 1, expand=True)
        df_squad[['Age','Jours']] = df_squad["Age"].str.split("-", 1, expand=True)
        df_squad[['Pos','Pos2']] = df_squad["Pos"].str.split(",", 1, expand=True)
        df_squad.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_squad.columns.values[15] = 'Gls/90'
        df_squad.columns.values[16] = 'Ast/90'
        df_squad.columns.values[17] = 'G+A/90'
        df_squad.columns.values[18] = 'G-PK/90'
        df_squad.columns.values[19] = 'G+A-PK/90'
        df_squad = df_squad[df_squad['Min'].notna()].fillna(0)

        #Scrape goalkeeper stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation and age.
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_gk = scrap.get_team_gk_stats(url)
        df_gk.columns = df_gk.columns.droplevel()
        df_gk.drop(df_gk.index[-2:], inplace=True)
        df_gk.drop('Matches', axis=1, inplace=True)
        df_gk[['Drapeau','Nation']] = df_gk["Nation"].str.split(" ", 1, expand=True)
        df_gk[['Age','Jours']] = df_gk["Age"].str.split("-", 1, expand=True)
        df_gk.drop(['Drapeau', 'Jours'], axis=1, inplace=True)
        df_gk = df_gk[df_gk['Min'].notna()].fillna(0)
        df_gk.columns.values[18] = 'PKatt-GK'
        df_gk.columns.values[22] = 'PKsv%'
        df_gk.drop(['Nation', 'Pos', 'Age', 'MP', 'Starts', 'Min', '90s'], inplace=True, axis=1)

        #Scrape shooting stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_shoot = scrap.get_team_shoot_stats(url)
        df_shoot.columns = df_shoot.columns.droplevel()
        df_shoot.drop(df_shoot.index[-2:], inplace=True)
        df_shoot.drop(['Matches', 'Dist'], axis=1, inplace=True)
        df_shoot[['Drapeau','Nation']] = df_shoot["Nation"].str.split(" ", 1, expand=True)
        df_shoot[['Age','Jours']] = df_shoot["Age"].str.split("-", 1, expand=True)
        df_shoot[['Pos','Pos2']] = df_shoot["Pos"].str.split(",", 1, expand=True)
        df_shoot.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_shoot = df_shoot[df_shoot['90s'].notna()].fillna(0)
        df_shoot.drop(['Nation', 'Pos', 'Age', '90s', 'Gls', 'PK', 'PKatt'], inplace=True, axis=1)

        #Scrape playing time stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_play = scrap.get_team_play_time(url)
        df_play.columns = df_play.columns.droplevel()
        df_play.drop(df_play.index[-2:], inplace=True)
        df_play.drop('Matches', axis=1, inplace=True)
        df_play[['Drapeau','Nation']] = df_play["Nation"].str.split(" ", 1, expand=True)
        df_play[['Age','Jours']] = df_play["Age"].str.split("-", 1, expand=True)
        df_play[['Pos','Pos2']] = df_play["Pos"].str.split(",", 1, expand=True)
        df_play.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_play = df_play[df_play['Min'].notna()].fillna(0)
        df_play.drop(['Nation', 'Pos', 'Age', 'MP', 'Starts', 'Min', '90s'], inplace=True, axis=1)

        #Scrape miscellaneous stats using a predefined function. 
        #Drop index level, total and subtotal rows, matches column. 
        #Clean nation, age and position (retaining the first only).
        #Drop players who didn't play a single minute this season
        #Fill NaN with 0
        #Drop future duplicated columns in the global DataFrame
        df_misc = scrap.get_team_misc_stats(url)
        df_misc.columns = df_misc.columns.droplevel()
        df_misc.drop(df_misc.index[-2:], inplace=True)
        df_misc.drop(['Matches', 'PKwon', 'PKcon'], axis=1, inplace=True)
        df_misc[['Drapeau','Nation']] = df_misc["Nation"].str.split(" ", 1, expand=True)
        df_misc[['Age','Jours']] = df_misc["Age"].str.split("-", 1, expand=True)
        df_misc[['Pos','Pos2']] = df_misc["Pos"].str.split(",", 1, expand=True)
        df_misc.drop(['Drapeau', 'Jours', 'Pos2'], axis=1, inplace=True)
        df_misc = df_misc[df_misc['90s'].notna()].fillna(0)
        df_misc.drop(['Nation', 'Pos', 'Age', '90s', 'CrdY', 'CrdR'], inplace=True, axis=1)

        #Merge DataFrames into a main one
        merge1 = pd.merge(df_squad, df_play, how='left', on=['Player'])
        merge2 = pd.merge(merge1, df_shoot, how='left', on=['Player'])
        merge3 = pd.merge(merge2, df_misc, how='left', on=['Player'])
        df_team = pd.merge(merge3, df_gk, how='left', on=['Player'])

        #Add a Club column based on the Teams name provided.
        #Put it as the 1st column
        df_team['Club'] = f"{teams}"
        first_column = df_team.pop('Club')
        df_team.insert(0, 'Club', first_column)
    
        #Return CSV containing stats for every single League Two teams and url provided
        df_team.to_csv(fr"{PATH}\League_Two_{teams}_stats.csv",index = True)


# In[41]:


#Function to concatenate the League stats per gameweek
#Need a PATH to the League Stats directory and the URL of the League
def get_concatenated_l2_stats(PATH, url):
    
    #Get all the csv files in the directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)
    
    #Add a Gameweek column
    result['End of Gameweek'] = scrap.get_last_gameweek(url)
    first_column = result.pop('End of Gameweek')
    result.insert(0, 'End of Gameweek', first_column)
    gameweek = result['End of Gameweek'][0]

    #print out to a new csv file
    result.to_csv(fr"{PATH}\Stats per GW\League_Two_Concatenated_Stats_GW{gameweek}.csv",index = False)


# In[42]:


#Function to get a concatenated file of all the League stats per gameweek
#Need a PATH to the concatenated League stats per gameweek
def global_l2_stats(PATH) :
    
    #Get all the csv files in the directory
    csvfiles = glob.glob(os.path.join(PATH, '*.csv'))

    #loop through the files
    dataframes = []
    for csvfile in csvfiles:
        df = pd.read_csv(csvfile)
        dataframes.append(df)

    #concatenate them all together
    result = pd.concat(dataframes, ignore_index=True)
    
    #print out to a new csv file
    result.to_csv(fr"{PATH}\Global L2 Stats\Global_League_Two_Stats.csv",index = False)


# # Obtenir le noms des clubs

# In[43]:


#Function to get the name of the Home Team from a match report
#Need match report url
def get_club_home(url) :
    
    global club_a
    global club_b
    
    #Split the url to get only the teams in a list
    club = url.split('/')[6]
    club = club.split('-')[:-5]

    #Depending on the length of the list and the known suffixes of the clubs, we assign one or many list items to a team's name
    if len(club) == 2 : #Ex : Sunderland vs Gillingham
        club_a = club[0] #Ex : Sunderland
        club_b = club[1] #Ex : Gillingham

    elif len(club) == 3 : #Ex : Rotherham United vs Sunderland
        if club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = club[2] #Ex : Sunderland
        elif club[2] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]) #Ex : Rotherham United
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = club[2] #Ex : Sunderland
        elif club[1] in ['AFC', 'afc'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 4 : #Ex : Rotherham United vs Oxford United
        if club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] and club[2] not in ['Green', 'green'] and club[3] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]) #Ex : Oxford United
        elif club[1] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = club[3] #Ex : Sunderland
        elif club[2] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]+' '+club[3]) #Ex : Milton Keynes Dons
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = (club[2]+' '+club[3]) #Ex : Rotherham United
        elif club[2] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 5 : #Ex : Rotherham United vs Milton Keynes Dons
        if club[1] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = (club[3]+' '+club[4]) #Ex : Rotherham United
        elif club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]+' '+club[4]) #Ex : Milton Keynes Dons
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = (club[2]+' '+club[3]+' '+club[4]) #Ex : Milton Keynes Dons
        elif club[3] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = (club[3]+' '+club[4]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 6 : #Ex : Milton Keynes Dons vs Forest Green Rovers
        club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
        club_b = (club[3]+' '+club[4]+' '+club[5]) #Ex : Forest Green Rovers
    
    #Return the Home Team name
    return club_a


# In[44]:


#Function to get the name of the Away Team from a match report
#Need match report url
def get_club_away(url) :
    
    global club_a
    global club_b
    
    #Split the url to get only the teams in a list
    club = url.split('/')[6]
    club = club.split('-')[:-5]

    #Depending on the length of the list and the known suffixes of the clubs, we assign one or many list items to a team's name
    if len(club) == 2 : #Ex : Sunderland vs Gillingham
        club_a = club[0] #Ex : Sunderland
        club_b = club[1] #Ex : Gillingham

    elif len(club) == 3 : #Ex : Rotherham United vs Sunderland
        if club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = club[2] #Ex : Sunderland
        elif club[2] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]) #Ex : Rotherham United
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = club[2] #Ex : Sunderland
        elif club[1] in ['AFC', 'afc'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 4 : #Ex : Rotherham United vs Oxford United
        if club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] and club[2] not in ['Green', 'green'] and club[3] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]) #Ex : Oxford United
        elif club[1] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = club[3] #Ex : Sunderland
        elif club[2] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = club[0] #Ex : Sunderland
            club_b = (club[1]+' '+club[2]+' '+club[3]) #Ex : Milton Keynes Dons
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = (club[2]+' '+club[3]) #Ex : Rotherham United
        elif club[2] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 5 : #Ex : Rotherham United vs Milton Keynes Dons
        if club[1] in ['North', 'north', 'Park', 'park', 'And', 'and', 'Green', 'green', 'Halifax', 'halifax', 'Keynes', 'keynes', 'Bromwich', 'bromwich', 'Lynn', 'lynn'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = (club[3]+' '+club[4]) #Ex : Rotherham United
        elif club[1] in ['Rangers', 'rangers', 'Forest', 'forest', 'Wood', 'wood', 'Moors', 'moors', 'Wanderers', 'wanderers', 'United', 'united', 'Albion', 'albion', 'Rovers', 'rovers', 'Town', 'town', 'Athletic', 'athletic', 'FC', 'Utd', 'utd', 'Argyle', 'argyle', 'Weds', 'weds', 'Wednesday', 'wednesday', 'Stanley', 'stanley', 'Ath', 'ath', 'City', 'city', 'Alexandra', 'alexandra', 'Vale', 'vale', 'County', 'county', 'Orient', 'orient'] :
            club_a = (club[0]+' '+club[1]) #Ex : Rotherham United
            club_b = (club[2]+' '+club[3]+' '+club[4]) #Ex : Milton Keynes Dons
        elif club[0] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]) #Ex : AFC Wimbledon
            club_b = (club[2]+' '+club[3]+' '+club[4]) #Ex : Milton Keynes Dons
        elif club[3] in ['AFC', 'afc'] :
            club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
            club_b = (club[3]+' '+club[4]) #Ex : AFC Wimbledon
        else :
            print('Erreur')

    elif len(club) == 6 : #Ex : Milton Keynes Dons vs Forest Green Rovers
        club_a = (club[0]+' '+club[1]+' '+club[2]) #Ex : Milton Keynes Dons
        club_b = (club[3]+' '+club[4]+' '+club[5]) #Ex : Forest Green Rovers
    
    #Return the Away Team name
    return club_b


# In[ ]:





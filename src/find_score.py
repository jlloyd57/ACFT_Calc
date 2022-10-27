# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:48:57 2022

@author: MaryClare
"""
import pandas as pd


def grab_age_range(age):
    """ 
    @brief Converts user age to string to correlate it to acft chart
    @param age - age of user
    @return a string age range
    """
    if age >= 17 and age <= 21:
        return "17-21"
    if age >= 22 and age <= 26:
        return "22-26"
    if age >= 27 and age <= 31:
        return "27-31"
    if age >= 32 and age <= 36:
        return "32-36"
    if age >= 37 and age <= 41:
        return "37-41"
    if age >= 42 and age <= 46:
        return "42-46"
    if age >= 47 and age <= 51:
        return "47-51"
    if age >= 52 and age <= 56:
        return "52-56"
    if age >= 57 and age <= 61:
        return "57-61"
    if age >= 62 and age <= 75:
        return "62+"
    else:
        print("ERROR in AGE RANGE")
        return None


def grab_event_file_sex(event, sex):
    """ 
    @brief Grabs the corresponding csv file for the user
    @param event - the fitness event
    @param sex - gender of the user
    @return ACFT CSV file 
    """
    if event == "DL":
        if sex == "M":
            return "../include/DL_M.csv"
        elif sex == "F":
            return "../include/DL_F.csv"
    if event == "SPT":
        if sex == "M":
            return "../include/SPT_M.csv"
        elif sex == "F":
            return "../include/SPT_F.csv"
    if event == "HRP":
        if sex == "M":
            return "../include/HRP_M.csv"
        elif sex == "F":
            return "../include/HRP_F.csv"
    if event == "SDC":
        if sex == "M":
            return "../include/SDC_M.csv"
        elif sex == "F":
            return "../include/SDC_F.csv"
    if event == "PLK":
        if sex == "M":
            return "../include/PLK_M.csv"
        elif sex == "F":
            return "../include/PLK_F.csv"
    if event == "2MR":
        if sex == "M":
            return "../include/2MR_M.csv"
        elif sex == "F":
            return "../include/2MR_F.csv"


def handle_intermediate_score_number(rawscore_column, Points_column, raw_score):
    """
    @brief Finds the users score when the raw score in the score chart doesn't directly correlate to a point number and needs to be rounded down
    @param rawscore_column - column in the acft score chart of raw scores for events
    @param Points_column - column in the acft where the points are listed
    @param raw_score - raw score user got on this event 
    """
    for val in range(len(rawscore_column)):
        if rawscore_column[val] == "---":
            next
        elif float(rawscore_column[val]) < raw_score:
            return val


def handle_intermediate_score_time(rawscore_column, Points_column, raw_score):
    """
    @brief Finds the users score when the raw score for a timed event in the score chart doesn't directly correlate to a point number and needs to be rounded down
    @param rawscore_column - column in the acft score chart of raw scores for events
    @param Points_column - column in the acft where the points are listed
    @param raw_score - raw score user got on this timed event 
    """
    for val in range(len(rawscore_column)):
        if rawscore_column[val] == "---":
            next
        elif float(rawscore_column[val]) > raw_score:
            return val


def convert_to_seconds(raw_score):
    """
    @brief converts a timed events raw score into seconds 
    @return the score in seconds 
    """
    print(raw_score)
    separator = raw_score.find(':')
    final_seconds = -1
    minutes = 0
    seconds = 0
    if separator == 2:
        if raw_score[0] == "0":
            minutes = int(raw_score[1])
        else:
            minutes = int(raw_score[:2])
        seconds = int(raw_score[3:])
        final_seconds = minutes*60 + seconds
    elif separator == 1:
        minutes = int(raw_score[0])
        seconds = int(raw_score[2:])
        final_seconds = minutes*60 + seconds
    return final_seconds


def score_event_number(event, age, sex, raw_score):
    """
    @brief finds the score for the given pt event
    @param event - pt event
    @param age - age of user taking acft
    @param sex - gender of user
    @param raw score - score of fitness event before it's calculated into a point value
    @return - calculated point value for this fitness event 
    """
    # Grab correct file based on sex and grab correct age range
    csv_path = grab_event_file_sex(event, sex)
    age_range = grab_age_range(age)

    final_score = -1

    # Grab DL and Points columns for information
    csv_read = pd.read_csv(csv_path)
    rawscore_column = csv_read[age_range]
    Points_column = csv_read['Points']

    # Find raw score in age column and find points that correspond
    point_location = -1
    for val in range(len(rawscore_column)):
        if rawscore_column[val] == str(raw_score):
            point_location = val
            break

    if point_location == -1:
        # Handle greater than Max value
        if float(rawscore_column[0]) < raw_score:
            print("Soldier exceeded standard! MAX score!")
            point_location = 0
        # Handle less than Min value
        elif float(rawscore_column[len(rawscore_column)-1]) > raw_score:
            print("Soldier did not meet minimum standard.")
            point_location = len(rawscore_column) - 1
        # Handle an intermediate value
        else:
            print("Soldier had an intermediate value. Round down for score.")
            point_location = handle_intermediate_score_number(
                rawscore_column, Points_column, raw_score)

    # Grab final score and return
    final_score = Points_column[point_location]
    return final_score


def score_event_time(event, age, sex, raw_score):
    """
    @brief finds the score for the given timed pt event
    @param event - pt event
    @param age - age of user taking acft
    @param sex - gender of user
    @param raw score - score of fitness event before it's calculated into a point value
    @return - calculated point value for this fitness event 
    """
    # Grab correct file based on sex and grab correct age range
    csv_path = grab_event_file_sex(event, sex)
    age_range = grab_age_range(age)

    final_score = -1

    # Grab DL and Points columns for information
    csv_read = pd.read_csv(csv_path)
    rawscore_column = csv_read[age_range]
    Points_column = csv_read['Points']

    raw_score = convert_to_seconds(raw_score)

    # Find raw score in age column and find points that correspond
    point_location = -1
    for val in range(len(rawscore_column)):
        if rawscore_column[val] == raw_score:
            point_location = val
            break
    if event == "PLK":
        if point_location == -1:
            # Handle greater than Max value
            if float(rawscore_column[0]) < raw_score:
                print("Soldier exceeded standard! MAX score!")
                point_location = 0
            # Handle less than Min value
            elif float(rawscore_column[len(rawscore_column)-1]) > raw_score:
                print("Soldier did not meet minimum standard.")
                point_location = len(rawscore_column) - 1
            # Handle an intermediate value
            else:
                print("Soldier had an intermediate value. Round down for score.")
                point_location = handle_intermediate_score_number(
                    rawscore_column, Points_column, raw_score)
    else:
        if point_location == -1:
            # Handle greater than Max value
            if float(rawscore_column[0]) > raw_score:
                print("Soldier exceeded standard! MAX score!")
                point_location = 0
            # Handle less than Min value
            elif float(rawscore_column[len(rawscore_column)-1]) < raw_score:
                print("Soldier did not meet minimum standard.")
                point_location = len(rawscore_column) - 1
                # Handle an intermediate value
            else:
                print("Soldier had an intermediate value. Round down for score.")
                point_location = handle_intermediate_score_time(
                    rawscore_column, Points_column, raw_score)

    # Grab final score and return
    final_score = Points_column[point_location]
    return final_score


def score_event(event, age, sex, raw_score):
    """
    @brief breaks down pt events into timed and number score events 
    @returns the score for the event 
    """
    if event == "SDC" or event == "2MR" or event == "PLK":
        return score_event_time(event, age, sex, raw_score)
    elif event == "DL" or event == "HRP" or event == "SPT":
        return score_event_number(event, age, sex, raw_score)

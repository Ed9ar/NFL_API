#!/usr/bin/env python3 

from flask import Flask
from flask import request, jsonify
from sportsreference.nfl.teams import Teams
from sportsreference.nfl.schedule import Schedule
import pandas as pd
import re
from datetime import datetime
from sportsreference.nfl.boxscore import Boxscores
from scipy import stats
from sportsreference.nfl.teams import Teams

scores = pd.read_csv("scores.csv")

app = Flask(__name__)

#La desviacion estandar para la victoria de un equipo es de 13.86

def calcWinner(home_team, away_team, teamStats, i, date):

    #normalizar valores 
    #Utilizamos el diferencial de puntos de ambos equipos para determinar por cuantos puntos se ganara el encuentro
    #normalizamos con el valor maximo de diferencial de puntos para un equipo en la temporada y utlizando  10 como nuestro nuevo maximo
    home_point = teamStats[teamStats.index.str.startswith(home_team)]['Margin of Victory'][0]
    away_point = teamStats[teamStats.index.str.startswith(away_team)]['Margin of Victory'][0]

    home_win_p = teamStats[teamStats.index.str.startswith(home_team)]['Win Percentage'][0]
    away_win_p = teamStats[teamStats.index.str.startswith(away_team)]['Win Percentage'][0]

    column_max = teamStats["Margin of Victory"]
    max_value = column_max.max()
    val_home = (home_point - away_point)*10 / max_value
    val_away = (away_point - home_point)*10/ max_value

    #se utiliza el valor de porcentaje de victoria para cada equipo
    win_home = stats.norm.sf(home_win_p, val_home, 13.86)
    
    #print(win_home)
    win_away = stats.norm.sf(away_win_p, val_away, 13.86)
    
    #print(win_away)

    if win_home > win_away:
        #print(str(home_team) + " tiene un " + str(win_home) + " de ganar el partido a " + str(away_team)) 
        if scores['score_home'][i] > scores['score_away'][i]:
            return 1, home_team, away_team, win_home, date
        else:
            return 0, home_team, away_team, win_home, date
    else:
        #print(str(away_team) + " tiene un " + str(win_away) + " de ganar el partido a " + str(home_team))
        if scores['score_away'][i] > scores['score_home'][i]:
            return 1,away_team, home_team, win_away, date
        else:
            return 0,away_team, home_team, win_away, date
    #obtener diferencial de yardas
    #presnentar diferencial de puntos
    #diferencial de turnovers
    
    
def teamSeasonStats(year):

    teamsdf_final = pd.DataFrame()
    teams = Teams(year)
    for team in teams:
        # assign data of lists.  
        data = {'Margin of Victory': team.margin_of_victory, 'Rank': team.rank,'Win Percentage':team.win_percentage, 'Turnovers': team.interceptions+team.fumbles, "Points_for": team.points_for, "Points_Against": team.points_against, "Ofensiva":team.offensive_simple_rating_system, "Defensiva": team.defensive_simple_rating_system, "Global": team.simple_rating_system}    
        team_df = pd.DataFrame(data, index=[team.name]) 
         
        teamsdf_final = pd.concat([teamsdf_final,team_df])
        
            
    return teamsdf_final


def match(year):

    predicciones_correctas = 0
    incorrectas = 0
    teams_df = teamSeasonStats(year)
    
    #print(teams_df)
    #aqui ver como se pueden sacar los partidos

    
    for i in range(len(scores)):
        num = calcWinner(scores['team_home'][i], scores['team_away'][i], teams_df, i, scores['schedule_date'][i])
        if num == 0:
            incorrectas+=1
        else:
            predicciones_correctas+=1
    
    #print("Se hicieron un total de predicciones : " + str(predicciones_correctas+incorrectas))
    #print("CORRECTAS: " + str(predicciones_correctas))
    #print("INCORRECTAS " + str(incorrectas))

    #print("EFICACIA "+ str((predicciones_correctas*100)/(predicciones_correctas+incorrectas))+ "%")
    
def team_prediction(team, year):
    teams_df = teamSeasonStats(year)
    
    #print(teams_df)
    #aqui ver como se pueden sacar los partidos
    team_info = []

    for i in range(len(scores)):
        num, winner, loser, win_prob, date = calcWinner(scores['team_home'][i], scores['team_away'][i], teams_df, i, scores['schedule_date'][i])
        if winner == team or loser == team:
            team_info.append([winner, win_prob, loser, date])
    
    return team_info

@app.route('/', methods=['GET'])
def home():
    return "Q-PRON"

@app.route('/api/v1/stats/nfl', methods=['GET'])
def api_stats():
    year = 2021
    teamdf = pd.DataFrame()
    team_matches = []
    if 'team' in request.args:
        team= request.args['team']
        print(team)
        team = re.sub(r"(\w)([A-Z])", r"\1 \2", team)
        teams = Teams(year)
        for te in teams:
            if team == te.name:
            # assign data of lists.  
                data = {'Margin of Victory': te.margin_of_victory, 'Rank': te.rank,'Win Percentage':te.win_percentage, 'Turnovers': te.interceptions+te.fumbles, "Points_for": te.points_for, "Points_Against": te.points_against, "Ofensiva":te.offensive_simple_rating_system, "Defensiva": te.defensive_simple_rating_system, "Global": te.simple_rating_system}    
    else:
        return "Error: No id field provided. Please specify an id."
    
    
    return jsonify(data)
    

# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/nfl', methods=['GET'])
def api_team():
    year = 2021
    #match(year)
    team_matches = []
    if 'team' in request.args:
        team= request.args['team']
        print(team)
        team = re.sub(r"(\w)([A-Z])", r"\1 \2", team)
        matches = team_prediction(team, 2021)
    else:
        return "Error: No id field provided. Please specify an id."
    
    
    for m in matches:
        team_matches.append({'winnner': m[0],
        'win_prob': m[1],
        'loser': m[2],
        'date': m[3]
        })
    return jsonify(team_matches)



app.run()

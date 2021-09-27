from sportsreference.nfl.teams import Teams
from sportsreference.nfl.schedule import Schedule
import pandas as pd

from datetime import datetime
from sportsreference.nfl.boxscore import Boxscores

from sportsreference.nfl.teams import Teams
from scipy import stats

scores = pd.read_csv("scores.csv")


#La desviacion estandar para la victoria de un equipo es de 13.86

def calcWinner(home_team, away_team, teamStats, i, dates):

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
        print(str(home_team) + " tiene un " + str(win_home) + " de ganar el partido a " + str(away_team)) 
        if scores['score_home'][i] > scores['score_away'][i]:
            return 1, home_team, away_team, win_home, dates
        else:
            return 0, home_team, away_team, win_home, dates
    else:
        print(str(away_team) + " tiene un " + str(win_away) + " de ganar el partido a " + str(home_team))
        if scores['score_away'][i] > scores['score_home'][i]:
            return 1,away_team, home_team, win_away, dates
        else:
            return 0,away_team, home_team, win_away, dates
    #obtener diferencial de yardas
    #presnentar diferencial de puntos
    #diferencial de turnovers
    
    
def teamSeasonStats(year):

    teamsdf_final = pd.DataFrame()
    teams = Teams(year)
    for team in teams:
        # assign data of lists.  
        data = {'Margin of Victory': team.margin_of_victory, 'Rank': team.rank,'Win Percentage':team.win_percentage, 'Turnovers': team.interceptions+team.fumbles}    
        team_df = pd.DataFrame(data, index=[team.name]) 
         
        teamsdf_final = pd.concat([teamsdf_final,team_df])
        
            
    return teamsdf_final


def match(year):

    predicciones_correctas = 0
    incorrectas = 0
    teams_df = teamSeasonStats(year)
    
    print(teams_df)
    #aqui ver como se pueden sacar los partidos

    
    for i in range(len(scores)):
        num = calcWinner(scores['team_home'][i], scores['team_away'][i], teams_df, i, scores['schedule_date'][i])
        if num == 0:
            incorrectas+=1
        else:
            predicciones_correctas+=1
    
    print("Se hicieron un total de predicciones : " + str(predicciones_correctas+incorrectas))
    print("CORRECTAS: " + str(predicciones_correctas))
    print("INCORRECTAS " + str(incorrectas))

    print("EFICACIA "+ str((predicciones_correctas*100)/(predicciones_correctas+incorrectas))+ "%")
    
def team_prediction(team, year):
    teams_df = teamSeasonStats(year)
    
    print(teams_df)
    #aqui ver como se pueden sacar los partidos
    team_info = []

    for i in range(len(scores)):
        num, winner, loser, win_prob, dates = calcWinner(scores['team_home'][i], scores['team_away'][i], teams_df, i,scores['schedule_date'][i])
        if winner == team or loser == team:
            team_info.append([winner, win_prob, loser, dates])
    
    return team_info

year = 2021



match(year)
print(team_prediction('Baltimore Ravens', 2021))





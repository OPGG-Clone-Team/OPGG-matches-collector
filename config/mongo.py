from pymongo import MongoClient,  IndexModel, ASCENDING, DESCENDING

def mongoClient(app):
  mongoClient = MongoClient(app.config["MONGO_URI"])
  create_initial_indexes(mongoClient.LEAGUEDATA)
  
  return mongoClient

# TODO - 인덱스설정 등 초기설정은 추후 따로 분리할 것
def create_initial_indexes(db):
  
  # league_entries
  league_entries_index = IndexModel([
    ("summonerId",ASCENDING), 
    ("summonerName", ASCENDING)
    ], name ="league_entries_index")
  
  summoners_index = IndexModel([
    ("puuid", ASCENDING),
    ("internal_name", ASCENDING)
  ], name = "summoners_index")
  
  summoner_matches_index = IndexModel([
    ("puuid", ASCENDING)
  ], name = "summoner_matches_index")
  
  matches_index = IndexModel([
    ("matchId", DESCENDING),
    ("gameCreation", DESCENDING),
  ], name = "matches_index")
  
  participants_index = IndexModel([
    ("matchId", DESCENDING),
    ("puuid", ASCENDING),
    ("teamId", ASCENDING),
  ],name = "participants_index")
  
  teams_index = IndexModel([
    ("matchId", DESCENDING),
    ("teamId", ASCENDING),
  ],name = "teams_index")
  
  timelines_index = IndexModel([
    ("matchId", DESCENDING),
    ("puuid", ASCENDING),
    ("teamId", ASCENDING),
    ("participantId", ASCENDING),
  ],name = "timelines_index")
  
  champion_statics_lane_index = IndexModel([
    ("championName", ASCENDING),
    ("plays", DESCENDING),
    ("win_rate", DESCENDING),
  ],name = "champion_statics_lane_index")
  
  champion_statics_index = IndexModel([
    ("championName", ASCENDING),
    ("plays", DESCENDING),
    ("win_rate", DESCENDING),
  ],name = "champion_statics_index")
  
  db.league_entries.create_indexes([league_entries_index])
  db.summoners.create_indexes([summoners_index])
  db.summoner_matches.create_indexes([summoner_matches_index])
  db.matches.create_indexes([matches_index])
  db.participants.create_indexes([participants_index])
  db.champion_statics_lane.create_indexes([champion_statics_lane_index])
  db.champion_statics.create_indexes([champion_statics_index])
  db.teams.create_indexes([teams_index])
  db.timelines.create_indexes([timelines_index])
  
  

      
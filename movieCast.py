import requests
import pandas as pd
import urllib.parse
import random


api_key = "d3a1b7a530cd142048fbe3572bc9302b"
movie_data = ''
actor_data = ''
role_data = ''
role_count_data = ''
    
def Movie_Cast(movieID, actorLimit=5):
    url = f"https://api.themoviedb.org/3/movie/{movieID}/credits?api_key={api_key}&language=en-US"
    actors = []
    rawRequest = requests.get(url).json()["cast"]
    rawRequest.sort(key=extract_popularity, reverse=True)
    for castMember in rawRequest[:actorLimit]:
        actors.append(castMember["id"])
    return actors

def Movie_Cast_CSV(movieID, actorLimit=5):
    global role_data
    global actor_data
    movie_cast = role_data[(role_data.imdb_title_id == movieID) & (role_data.ordering <= actorLimit)]
    actors = []
    for index, castMember in movie_cast.iterrows():
        actors.append(castMember["imdb_name_id"])
    return actors

def Movie_Name(movieID):
    url = f"https://api.themoviedb.org/3/movie/{movieID}?api_key={api_key}&language=en-US"
    r = requests.get(url).json()["title"]
    return r

def Actor_Movies(actorID):
    url = f"https://api.themoviedb.org/3/person/{actorID}/movie_credits?api_key={api_key}&language=en-US"
    r = requests.get(url).json()["cast"]
    movieList = {}
    for movie in r:
        movieList[movie["id"]] = movie["title"]
    return movieList

def Actor_Movies_CSV(actorID):
    global role_data
    global movie_data
    global actor_data
    actor_name = actor_data[actor_data.imdb_name_id == actorID].iloc[0]["name"]
    print(f"\nAnalyzing {actor_name}'s filmography..")
    actorMovieList = role_data[role_data["imdb_name_id"] == actorID]
    actorMovieList_named = pd.merge(actorMovieList, movie_data, on="imdb_title_id")
    actorMovieList_named = actorMovieList_named[actorMovieList_named.metascore.notnull()]
    actorMovieList_named.sort_values(by=['worlwide_gross_income'], ascending=False)
    movieList = {}
    for index, movie in actorMovieList_named.iterrows():
        movieList[movie["imdb_title_id"]] = movie["title"]
    return movieList
 
def Get_All_Data():
    print("\nLoading movie data...")
    global movie_data
    movie_data = pd.read_csv("C:/sloan/CodeSnips/movies.csv")
    
    print("\nLoading actor data...")    
    global actor_data
    actor_data = pd.read_csv("C:/sloan/CodeSnips/actors.csv")
    
    print("\nLoading cast data...\n")    
    global role_data
    role_data = pd.read_csv("C:/sloan/CodeSnips/casts.csv")

    global role_count_data
    role_count_data = role_data.groupby(["imdb_name_id"]).size().reset_index(name='role_count')
    
    actor_data = pd.merge(actor_data, role_count_data, on="imdb_name_id") # add counts of roles for each actor
    
    print(actor_data[(actor_data.role_count > 80) & (actor_data.date_of_birth > "1950-01-01")].sample(n=10))

    print("-----------------------")
    print("Data loading complete!")
    print("-----------------------")
    

def Actor_CoStars(actorID):
    movies = Actor_Movies(actorID)
    print(str(len(movies)) + " movies being analyzed for this actor...")
    costars = {}
    for movieID, movieName in movies.items():
        print(movieName + "...")
        movieCast = Movie_Cast(movieID, 7)
        for castMember in movieCast:
            isActor = castMember == actorID
            if castMember not in costars.keys() and not isActor:
                costars[castMember] = [movieID]
            elif not isActor:
                costars[castMember].append(movieID)
    return costars

def GetActorDetails():
    global actor_data
    done = False
    while not done:
        actorIndex = input("enter actor id: ")
        actorRow = actor_data[actor_data.imdb_name_id == actorIndex]
        print(actorRow.head())
        done = True if input("type 'e' then enter to exit.") == "e" else False

def Random_Actor():
    global actor_data
    qualified_actors = actor_data[(actor_data.role_count > 40) & (actor_data.date_of_birth > "1950-01-01")]
    rand_actors = qualified_actors.sample(n=5)
    print(rand_actors.head())
    return rand_actors

def Actor_CoStars_CSV(actorID):
    movies = Actor_Movies_CSV(actorID)
    print(str(len(movies)) + " movies being analyzed for this actor...")
    print("----------------------------------")
    costars = {}
    for movieID, movieName in movies.items():
        # print(movieName + "...")
        movieCast = Movie_Cast_CSV(movieID, 5)
        for castMember in movieCast:
            isActor = castMember == actorID
            if castMember not in costars.keys() and not isActor:
                costars[castMember] = [movieID]
            elif not isActor:
                costars[castMember].append(movieID)
    return costars

def MovieSearch():
    search = input("search a movie title: ")
    searchstringEncoded = urllib.parse.quote(str(search))
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&page=1&query={searchstringEncoded}"
    r = requests.get(url).json()["results"]
    movieMatches = {}
    for movie in r:
        movieMatches[movie["id"]] = movie["title"]
    return movieMatches

class Actor:
    def __init__(self, name, id, popularity = None):
        self.name = name
        self.id = id
        self.popularity = popularity

def ActorSearch():
    actorSearch = input("search an actor. if you want a random actor, type 'r' then enter to': ")
    searchstringEncoded = urllib.parse.quote(str(actorSearch))
    url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&page=1&query={searchstringEncoded}"
    r = requests.get(url).json()["results"]
    i = 1
    print("-------------")
    for actor in r:
        print(str(i) + ". " + actor["name"])
        i = i + 1
    actorExact = input("type the number of the actor matching your search: ")
    if int(actorExact) <= i:
        actorRow = r[int(actorExact) - 1]
        actorObj = Actor(actorRow["name"], actorRow["id"], actorRow["popularity"] )
        print("\nGot it!\n")
        return actorObj

def ActorSearch_CSV():
    global actor_data
    satisfied = False
    while not satisfied:
        actorSearch = input("search an actor, or type 'r' then enter to select a random actor: ").lower()
        filteredResults = ''
        if actorSearch == "r":
            filteredResults = Random_Actor()
        else:
            filteredResults = actor_data[actor_data["name"].str.lower().str.contains(actorSearch)]
        i = 1
        print("-------------") 
        for index, actor in filteredResults.iterrows():
            print(str(i) + ". " + actor["name"])
            i = i + 1
        actorExact = input("type the number of the actor matching your search, or press 'n' to start a new search: ")
        if actorExact == "n":
            continue
        elif int(actorExact) <= i:
            actorObj = Actor(filteredResults["name"].iloc[int(actorExact) - 1], filteredResults["imdb_name_id"].iloc[int(actorExact) - 1])
            print("\nGot it!\n")
            satisfied = True
            return actorObj

def SearchTwoActors_CSV():
    print("\n Let's find your first actor. \n")
    actor1 = ActorSearch_CSV()
    print("\n Time for actor #2. \n")    
    actor2 = ActorSearch_CSV()
    print ("\nNice. Now that your actors are selected, we'll get to work finding " +
           "a connection between their films.\n")
    return actor1, actor2

def SearchTwoActors():
    print("\n Let's find your first actor. \n")
    actor1 = ActorSearch()
    print("\n Time for actor #2. \n")    
    actor2 = ActorSearch()
    print ("\nNice. Now that your actors are selected, we'll get to work finding " +
           "a connection between their films.\n")
    return actor1, actor2

def GetCommonMovies(actor1, actor2):
    actor1Movies = Actor_Movies(actor1).keys()
    actor2Movies = Actor_Movies(actor2).keys()
    crossover = list(set(actor1Movies) & set(actor2Movies))
    return crossover
  
def extract_popularity(json):
    try:
        return json['popularity']
    except KeyError:
        return 0

def Build_Actor_Connector_Final(parentDictionary, actor1, actor2, degrees):
    print(actor1, actor2, degrees)
    global actor_data
    global movie_data
    actor1_name = actor_data[actor_data.imdb_name_id == actor1].iloc[0]["name"]
    print(actor1_name)
    actor2_name = actor_data[actor_data.imdb_name_id == actor2].iloc[0]["name"]
    temp_parent = parentDictionary[actor2][0]
    temp_movies = parentDictionary[actor2][1]
    temp_actor = actor2
    
    connection_story = f"{actor1_name} and {actor2_name} are {degrees} degrees apart.\n\n"
    print(connection_story)
    while temp_actor != actor1:
        actor_name = actor_data[actor_data.imdb_name_id == temp_actor].iloc[0]["name"]
        parent_name = actor_data[actor_data.imdb_name_id == temp_parent].iloc[0]["name"]
        temp_movie_name = movie_data[movie_data.imdb_title_id == temp_movies[0]].iloc[0]["title"]
        connection_story += actor_name + " & " + parent_name + ": \n" + temp_movie_name + "\n" + "--------------------------------\n" 
        temp_actor = temp_parent
        temp_parent = "0" if temp_actor == actor1 else parentDictionary[temp_actor][0]
        temp_movies = "0" if temp_actor == actor1 else parentDictionary[temp_actor][1]
    print(connection_story)    
    
class Connect_Actors:
    def __init__(self):
        actor1, actor2 = SearchTwoActors_CSV()
        actor1_neighbors = Actor_CoStars_CSV(actor1.id)
        if actor2.id in actor1_neighbors.keys():
            shared_movies = str(len(actor1_neighbors[actor2.id]))
            add_s = "" if shared_movies == 1 else "s"
            print(f"\n{actor1.name} and {actor2.name} are 1 degree apart because " +
                  f"they appeared in {shared_movies} movie{add_s} together: \n")
            for movie in actor1_neighbors[actor2.id]:
                print(Movie_Name(movie))
        else:
            degreesAway, parent, matchingActor = BuildActorNetwork({actor1.id : actor1_neighbors}, actor1.id, actor2.id)
            if str(matchingActor) == "0":
                print("You stumped me! There are no connections between these actors.")
            else:
                Build_Actor_Connector_Final(parent, actor1.id, actor2.id, degreesAway)
 
def BuildActorNetwork(graph, vertex, vertexTarget):
    """ 
    
    BFS (breadth-first search) algorithm to traverse actor number 1's
    co-stars and then traverse each one of those actors' costar networks
    until a match with actor 2 is found. guarantees shortest distance.
    
    """
    queue = [vertex] # the queue is the list of actors that we loop through to find their co-stars.
    level = {vertex: 0} # this is a dictionary of actors that have been checked and their distance from actor 1
    parent = {vertex: None}  # this is a dictionary of actors and their parent actors (as well as the movie(s)
                             # that they and their parent were in together)
    while queue:
        v = queue.pop(0)  #get the first item from the queue and remove it
        if v not in graph:
            graph[v] = Actor_CoStars_CSV(v)
        for actor, movie in graph[v].items():    #index into the network of actor v to get co-stars
            if actor not in level:  #if the first neighbor of said actor hasn't been analyzed yet, proceed
                queue.append(actor)  #add this neighbor to the back of the queue to analyze their neighbors if necessary
                level[actor] = level[v] + 1  #add this neighbor to the level dictionary indicating how far they are from actor 1
                parent[actor] = [v, movie]  # add this neighbor to parent dictionary along with their parent actor
                if actor == vertexTarget:  # this is where we actually check if the given neighbor matches actor 2. 
                    print("\nfound a match!\n")
                    return level[v] + 1, parent, actor
                  #if no match is found, we have to add this neighbor's actors to the graph to traverse
    return level, parent, 0
    
# Defining main function 
def main(): 
    Get_All_Data()
    running = True
    while running:
        cnxn_instance = Connect_Actors()
        exitFunc = input("If you'd like to exit, press enter. Otherwise, press any key.")
        if exitFunc == "":
            running = False
    # GetActorDetails()
    
# Using the special variable  
# __name__ 
if __name__=="__main__": 
    main() 
    

import csv
import sys
import time

from math import ceil
from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    start_loading_time = time.time()
    load_data(directory)
    print("\n--- Loading time: %s seconds ---" % round(time.time() - start_loading_time, 3))

    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")
    if source == target:
        sys.exit("Source and target must be different")
    
    # ----------- User choose in what degree interrup program ----------
    max_degree = int(input("Degree (between 2-12): "))
    while max_degree > 12 or max_degree < 2:
        max_degree = int(input("Degree (between 2-12): "))

    # ----------- To track searching time --------------------------
    start_time = time.time()
    # --------------------------------------------------------------
    
    path = shortest_path(source, target, max_degree)
    print()
    
    if path is None:
        print(f"Not connected in {max_degree} degrees or least.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.") 
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

    print("\n--- %s seconds ---" % round(time.time() - start_time, 3))

def shortest_path(source, target, max_degree):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    
    # --------- Max degree for each frontier -------------
    if max_degree % 2 == 0:
        source_degree = max_degree / 2
        target_degree = max_degree
    else:
        target_degree = ceil(max_degree/2)
        source_degree = max_degree - target_degree

    # ----------- To switch between source and target nodes each degree ---- 
    starting_degree = 1

    # ------------------ Explore close nodes to source ---------------------
    initial_state = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()    
    counter = 1
    frontier.add(initial_state)
    
    # ------------------ Explore close nodes to target ---------------------
    target_state = Node(state=target, parent=None, action=None)
    frontier_target = QueueFrontier()
    frontier_target.add(target_state)
    explored_target = False

    # ---------------- Searching loop for each node ---------------------
    while True:
        
        if not explored_target:
            if frontier.empty():
                return None
            node = frontier.remove()
        else:
            if frontier_target.empty():
                return None
            node = frontier_target.remove()

        neighbors = neighbors_for_person(node.state)
        for neighbor in neighbors:
            
            if not explored_target:
                    if frontier_target.contains_state(neighbor[1]):
                            path = []                        
                            
                        # ----- Connection between source node and target node -------
                            for movie in people[node.state]['movies']:
                                if movie in people[neighbor[1]]['movies']:
                                    action = movie, neighbor[1]
                                    path.append(action)
                                    break
                            
                        # -------------- Track path of target node -----------------                            
                            node_frontier = frontier_target.get_node(neighbor[1])
                            while node_frontier.parent is not None:
                                print(node_frontier.state)
                                action_made = node_frontier.action
                                node_frontier = node_frontier.parent
                                action = action_made, node_frontier.state                                               
                                path.append(action)
                                
                                if node_frontier.state == target:
                                    break
                            
                            path.reverse()
                            print(path)
                            if checkIfDuplicates(path):
                                path.pop()  
                                
                                                 
                        # -------------- Track path of source node ---------------------          
                            while node.parent is not None:
                                action = node.action, node.state
                                path.append(action)
                                node = node.parent
                            
                            path.reverse()
                            print("after", path)
                            return path
                        # ------------------------------------------------------------
                            
                    if frontier.contains_state(neighbor[1]): 
                        continue  
                     
                    if neighbor[1] == target: 
                        path = []
                        node = Node(state=neighbor[1], parent=node, action=neighbor[0])
                        while node.parent is not None:
                            action = node.action, node.state
                            node = node.parent
                            path.append(action)
                                                
                        path.reverse()
                        return path

                    else:   
                        frontier.add(Node(state=neighbor[1], parent=node, action=neighbor[0])) 
                
            else:
                if frontier.contains_state(neighbor[1]):
                    path = []                    
                    
                    # ----- Connection between source node and target node -------
                    for movie in people[node.state]['movies']:
                        if movie in people[neighbor[1]]['movies']:
                            action = movie, node.state
                            path.append(action)
                            break
                    
                    # -------------- Track path of target node -----------------
                    while node.parent is not None:
                        action_made = node.action
                        node = node.parent
                        action = action_made, node.state                                               
                        path.append(action)

                        if node.state == target:
                            break                
                    
                    path.reverse()
                    node = frontier.get_node(neighbor[1])
                    
                    # -------------- Track path of source node ---------------------    
                    while node.parent is not None:
                        action = node.action, node.state
                        path.append(action)
                        node = node.parent
                    
                    path.reverse()
                    return path
                
                    # -----------------------------------------------------------------
                    
                elif frontier_target.contains_state(neighbor[1]):
                    continue
                else: 
                    frontier_target.add(Node(state=neighbor[1], parent=node, action=neighbor[0]))                 
        
        
        # ------ Intercale searching between source and target each degree ----------
        
        valor = degrees(node)
        
        if valor > source_degree and not explored_target:
            explored_target = True
        
        elif valor > starting_degree and not explored_target:
            explored_target = True
        
        elif valor > starting_degree and explored_target:
            starting_degree += 1
            explored_target = False
            
        elif valor > target_degree and explored_target:
            return None
        
        
        # --------------- Track how much nodes and degrees have explored --------------
        counter += 1
        if counter % 100 == 0:
            sys.stdout.write(f"\rNodes: {counter}, degree {degrees(node)}")
            sys.stdout.flush()


def checkIfDuplicates(listOfElems):
    """ Check if given list contains any duplicates,
        In this case to avoid repeated elements in the
        path 
    """ 
    setOfElems = set()
    for elemA, elemB in listOfElems:
        if elemA in setOfElems:
            return True
        else:
            setOfElems.add(elemA)         
    return False
    
def degrees(node):
    """ 
    Calculate degree of a given node 
    """
    count = 1
    while node.parent is not None:
        count += 1
        node = node.parent    
    return count

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for p_id in movies[movie_id]["stars"]:
            if p_id == person_id:
                continue
            neighbors.add((movie_id, p_id))
    return neighbors


if __name__ == "__main__":
    main()

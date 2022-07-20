from datetime import timedelta, datetime
import math
import sys
import numpy
import random

#parametry wykorzystywane przy obliczeniach
Num_vertices=100
min_weight=1
max_weight=100
min_edges=5
max_edges=15
runing_T= 60 # w sekundach
amount_of_ants=100
Solutions=5
penalty=5
ph_evaporate_rate=0.3
ph_use_chance=0.3
Alpha=1.75
Beta=0.4
smooth=20
smooth_limit=35


def Graph_generate():
    Graph = numpy.zeros((Num_vertices, Num_vertices), dtype=numpy.uintp)
    for i in range(1, Num_vertices):
        variable=random.randint(min_weight, max_weight) 
        Graph[i-1][i] = variable
        Graph[i][i-1] = variable  

    for i in range(Num_vertices):
        comp = min_edges - len(Graph[i].nonzero()[0])   
        if comp > 0:
            for _ in range(comp):
                another = set(range(Num_vertices)) - set(Graph[i].nonzero()[0]) - {i}
                while another:
                    j = random.choice(tuple(another))
                    if len(Graph[:, j].nonzero()[0]) < max_edges:
                        Graph[i][j] = Graph[j][i] = random.randint(min_weight, max_weight)
                        break
                    another.remove(j)
                else:
                    raise Exception('Failed to creat graph')
    return Graph

# stworzenia grafów 
matrix = Graph_generate()
ph_matrix = numpy.zeros((Num_vertices, Num_vertices), dtype=float)  # tworzenia grafu z feromonami
ph_matrix[matrix.nonzero()] = 1    
pro_matrix = numpy.zeros((Num_vertices, Num_vertices), dtype=float)  #tworzenie grafu prawdopodobieństwa
pro_matrix = numpy.copy(ph_matrix)


def Cost_calculator(graph, path):
    wagi = 0

    for a in range(0, len(path) - 2):
        if graph[path[a], path[a + 1]] > graph[path[a + 1], path[a + 2]]:
            wagi += (graph[path[a], path[a + 1]] * penalty)
        else:
            wagi += graph[path[a], path[a + 1]]
    return wagi



def Who_let_the_ants_out():    

    path = [random.randrange(0, Num_vertices)] 
    using_pheromone = random.random() < ph_use_chance   
    empty = set(range(Num_vertices)) - {path[0]}

    while empty:  
        friends = matrix[path[-1]].nonzero()[0]       
        unvisited_friends = tuple(empty & set(friends))        
        if unvisited_friends:
            if using_pheromone:               
                empty_propabilities = numpy.zeros(Num_vertices)
                empty_propabilities[unvisited_friends,] = \
                    pro_matrix[path[-1], unvisited_friends]                
                nex_t = random.choices(list(range(0, Num_vertices)),
                                          weights=empty_propabilities)[0]
            else:               
                nex_t = random.choice(unvisited_friends)
        else:
            if using_pheromone:                
                nex_t = random.choices(list(range(0, Num_vertices)), weights=pro_matrix[path[-1]])[0]                                          
            else:                
                nex_t = random.choice(friends)
        if nex_t in empty:
            empty.remove(nex_t)
        path.append(nex_t)

    return Cost_calculator(matrix, path), path


if __name__ == "__main__":

  the_best_solution = None
  stop = datetime.now() + timedelta(seconds=runing_T)
  while datetime.now() < stop:
    Paths = []
    # puszczamy mrówki - każda mrówka robi jedna sciezke i dodajemy je do listy 'paths'
    for i in range(amount_of_ants):
      Paths.append(Who_let_the_ants_out())

    Paths = sorted(Paths, key=lambda x: x[0]) # Sortujemy paths po koszcie
    best_paths = Paths[:Solutions] 


    # Aktualizacja feromonów, dodajemy wartości pomiędzy 0.1-1
    difference = best_paths[-1][0] - best_paths[0][0]
    for cost, path in best_paths:
      if difference:
        ph_power = (cost - best_paths[0][0]) / difference * 0.9
      else:
        ph_power = 1

      for j in range(0, len(path) - 1):
        k, l = path[j:j+2]
        ph_matrix[k, l] += 1 - ph_power


    # Parowanie feromonów -
    ph_matrix *= 1 - ph_evaporate_rate


    # Aktualizacja prawdopodobieństw
    pro_matrix = (ph_matrix ** Alpha)
    pro_matrix *= (matrix / 1) ** Beta


    # Wygładzanie
    for line in ph_matrix:
      if numpy.where(line > smooth_limit)[0].size:
        mini = line[line.nonzero()].min()
        for i, x in enumerate(line):
          if x > 0:
            line[i] = mini * (1 + math.log(x / mini, smooth))


    ph_use_chance += 0.0002

    if not the_best_solution or Paths[0][0] < the_best_solution:
      the_best_solution = Paths[0][0]
      print(f'Path with the lowest cost: {the_best_solution} at time: {datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}')


print('Parameters choosen by user:')
print(f'Running time of the algorithm: {runing_T} | number of ants: {amount_of_ants} | number of possible solutions: {Solutions} | pheromone evaporate rate: {ph_evaporate_rate} | propability of pheromone usage: {ph_use_chance} | alpha: {Alpha} | Beta: {Beta} | min edges: {min_edges} | max edges: {max_edges} | penalty parametr: {penalty}')
print(f'Cost for the best path is {the_best_solution}.')
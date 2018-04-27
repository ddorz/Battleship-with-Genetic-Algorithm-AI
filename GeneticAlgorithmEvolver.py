
from GeneticAlgorithm import GeneticAI
import numpy as np
from GridPresenter import GridController
from BattleshipAI import AI
import operator
import itertools
import random
from copy import deepcopy
import time

class GeneticAIEvolver(object):

    def __init__(self, populationSize, generations, numoffitnessloops=4):
        self._popSize = populationSize
        self._genCount = generations
        self._population = []
        self._generationalFitness = []
        self._numOfFitnessLoops = numoffitnessloops

    def Initalize_Generation(self):
        for i in range(self._popSize):
            ai = self._generate_random_individual()
            self._population.append(ai)

    def _generate_random_individual(self):
        # gene1 = 0.01 * np.random.randint(10, size=(GeneticAI.INPUT_LAYER, GeneticAI.HIDDEN_LAYER)) + 1
        # gene2 = 0.01 * np.random.randint(10, size=(GeneticAI.HIDDEN_LAYER, 1)) + 1
        # np.random.randn(5,100) * np.sqrt(2/100)
        gene1 = np.random.randn(GeneticAI.INPUT_LAYER, GeneticAI.HIDDEN_LAYER) * 0.1
        gene2 = np.random.randn(GeneticAI.HIDDEN_LAYER, 1) * 0.1
        return GeneticAI(gene1, gene2)

    def Simulate_Generations(self):
        t0 = time.time()
        rankedPopulation = self._rank_population_by_fitness()
        self._generationalFitness += [rankedPopulation[:]]
        t1 = time.time()
        print("Gen 0. Took " + format(t1-t0, '.2f') + "s. Best fitness: " + str(rankedPopulation[0][1]) + ". Average fitness: " + str(sum(n for _, n in rankedPopulation) / (self._popSize)))

        for i in range(1, self._genCount+1):

            t0 = time.time()
            fourth = int(self._popSize / 4)
            cutPopulation = rankedPopulation[:fourth]

            newPopulation = [self._population[x[0]] for x in cutPopulation]

            mutatedPopulation = self.perform_crossover_and_mutation(newPopulation)
            self._population = mutatedPopulation

            rankedPopulation = self._rank_population_by_fitness()
            self._generationalFitness += [rankedPopulation[:]]
            t1 = time.time()
            print("Gen " + str(i) + ". Took " + format(t1-t0, '.2f') + "s. Best fitness: " + str(rankedPopulation[0][1]) + ". Average fitness: " + str(sum(n for _, n in rankedPopulation) / (self._popSize)))

    def perform_crossover_and_mutation(self, population):
        # Immediately keep first 16th
        newPop = population[:int(len(population)/2)]

        # Create Mutant copy of top fourth
        for individual in newPop[:int(len(newPop))]:
            genes1 = self.mutate(individual.genes1, num=4)
            genes2 = self.mutate(individual.genes2, num=1)
            ai = GeneticAI(genes1, genes2)
            newPop.append(ai)

        # Using entire genepool create until back at population size
        genePool = list(itertools.combinations(population, 2))
        random.shuffle(genePool)
        for pair in genePool[:self._popSize-len(newPop)]:
            genes1 = self.gene_crossover(pair[0].genes1, pair[1].genes1)
            genes2 = self.gene_crossover(pair[0].genes2, pair[1].genes2)
            genes1 = self.mutate(genes1, num=4)
            genes2 = self.mutate(genes2, num=1)
            ai = GeneticAI(genes1, genes2)
            newPop.append(ai)

        return newPop

    """ Alters phenotypes by multiplying them by adding random small value.
    """
    def mutate(self, gene, num=5):
        indices = list(np.ndindex(gene.shape))
        np.random.shuffle(indices)
        indices = indices[:num]

        for i in indices:
            gene[i] = gene[i] + random.uniform(-0.01, 0.01)

        return gene

    """ Perform gene crossover on two genes.
        Makes a copy of gene1 to new gene. Iterates over gene2.
        Flips a coin to replace the value in the new gene.
    """
    def gene_crossover(self, gene1, gene2):
        newGene = np.array(gene1)

        for (x, y), value in np.ndenumerate(gene2):
            if bool(random.getrandbits(1)):
                newGene[x][y] = value

        return newGene

    """ Runs each individual of the population though fitness test 4 times.
        Then uses these results to sort and return the population.
    """
    def _rank_population_by_fitness(self):
        ranks = {}
        controllerTemplates = []

        all_coords = list(itertools.product(list(range(10)), repeat=2))
        while len(controllerTemplates) < self._numOfFitnessLoops + 1:
            gController = GridController(10)
            ai = AI(aiGridController=gController)
            ai.place_all_ships()
            random.shuffle(all_coords)
            for i in all_coords[:random.randint(30, 80)]:
                xCoord = i[0]
                yCoord = i[1]
                gController.process_shot(xCoord, yCoord)
            if gController.num_sunk() < 2:
                controllerTemplates.append(gController)

        for i in range(len(self._population)):
            fitness = self.run_fitness_on_multiple(self._population[i], controllers=controllerTemplates)
            ranks[i] = fitness

        sortedRanks = sorted(ranks.items(), key=operator.itemgetter(1))

        return sortedRanks

    def get_best_AI(self):
        sortedPopulation = [self._population[x[0]] for x in self._generationalFitness[-1]]
        return sortedPopulation[0].genes1, sortedPopulation[0].genes2

    def get_generational_fitness_list(self):
        return self._generationalFitness


    def run_fitness_on_multiple(self, ai, controllers=[], randomControllers=0, outputInfo=False, limit=10):
        gameStates = []
        if controllers == [] and randomControllers != 0:
            for i in range(randomControllers):
                gController = GridController(10)
                tempAI = AI(aiGridController=gController)
                tempAI.place_all_ships()
                gameStates.append(gController)
        else:
            for i in controllers:
                gController = deepcopy(i)
                gameStates.append(gController)

        fitness = []
        for state in gameStates:
            fitness += [ai.evaluate_fitness_for_gameState(state, limit=limit)]

        fitMin = min(fitness)
        fitMax = max(fitness)
        fitAve = sum(fitness) / len(fitness)
        if outputInfo:
            print("Min: " + str(fitMin) + ". " + "Max: " + str(fitMax) + ". "  + "Average: " + str(fitAve) + ". " + str(fitness))

        if 100 in fitness:
            return 100

        return (fitAve + fitMin) / 2

    def getentirepopulation(self):
        return self._population

# Run Genetic Algorithm Evolver
if __name__ == "__main__":
    evolver = GeneticAIEvolver(100, 200, numoffitnessloops=5)
    evolver.Initalize_Generation()
    evolver.Simulate_Generations()

    population = evolver.getentirepopulation()
    bestAvg = 100
    best = population[0]
    decent = []
    iterator = 0
    for p in population:
        print(str(iterator))
        iterator += 1
        avg = evolver.run_fitness_on_multiple(p, randomControllers=4, limit=-1, outputInfo=True)
        if avg < bestAvg:
            bestMax = avg
            best = p

    fitnessList = evolver.get_generational_fitness_list()
    for i in range(len(fitnessList)):
        np.savetxt("GeneticAI/gen" + str(i) + ".csv", np.array(fitnessList[i]).astype(int), fmt='%i', delimiter=',')

    np.savetxt("GeneticAI/genes1.csv", best.genes1, delimiter=",")
    np.savetxt("GeneticAI/genes2.csv", best.genes2, delimiter=",")

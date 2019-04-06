import random
from typing import NamedTuple
from typing import List

class Gene(NamedTuple):
    a: bool
    b: bool

class Genome(NamedTuple):
    appearance: List[Gene]
    fancy: List[Gene]
    miscarry: List[Gene]
    other: List[Gene]
    is_male: bool
    is_neanderthal: bool
    birthday: int

NUMBER_OF_APPEARANCE_GENES = 20
NUMBER_OF_FANCY_GENES = 20
NUMBER_OF_MISCARRY_GENES = 20
NUMBER_OF_OTHER_GENES = 20

def one_breeding_cycle(population: List[Genome], cycle: int, pool_size: int):
    '''Executes one breeding cycle, given a population of mixed species

    Args:
        population: list of individuals. Modified in situ
        cycle: which breeding cycle is this? (starts at one and increments)
        pool_size: how many partners to consider when finding the best  

    Returns:
        None: The input population is modified in situ.

    '''

    # We expect some proportion of the available females to breed
    BREEDING_PROPORTION = 0.5
    females = reproductive(population, False, cycle)
    unmated_females = int(len(females) * BREEDING_PROPORTION)
    males = reproductive(population, True, cycle)

    # Fetch the correct number of breeding pairs from the population. Females are
    # removed, as they can only get pregnant once. Males are left.
    while len(females) > unmated_females:
        (female, male) = breeding_pair(females, males, pool_size)
        child = breed(male, female, cycle)
        if not miscarry(child):
            population.append(child)

    return None

def breed(male: Genome, female: Genome, cycle: int) -> Genome:
    '''Mix up the genes of a male and female to make a child

    Args:
        male:
        female:
        cycle: Which breeding cycle this is 
    
    Return:
        The child (which may not be viable)
    '''
        
    is_male = random.randint(0, 1) == 0 # assume equal probability of boy or girl
    return Genome(
        merge(male.appearance, female.appearance),
        merge(male.fancy, female.fancy),
        merge(male.miscarry, female.miscarry),
        merge(male.other, female.other),
        is_male,
        male.is_neanderthal,
        cycle)

def miscarry(child: Genome):
    '''Will the given child spontaneously abort?

    Checks whether the foetus is male and carries the neanderthal Y-chromosome.

    We make the simplifying assumption that the miscarriage-causing genes are
    equally spread among all genes, so whether a miscarriage occurs is a
    probabilistic function of the proportion of sapiens-ness, with 100% probability
    for sapiens and 0% probability for neanderthal. The shape of the function, and
    the Monte-Carlo draws that define instances are internal to this function.

    Args:
        child: The child that may miscarry

    Returns:
        bool: true if there is miscarriage, or false if the pregnancy runs to term.

    '''

    if not child.is_male:
        return False
    if not child.is_neanderthal:
        return False 

    # We assume that the child will always miscarry if there are any miscarriage
    # genes in the genome. (Assume dominant gene.)
    return count_genes(child.miscarry) > 0

def breeding_pair(females: List[Genome], males: List[Genome], pool_size) -> (Genome, Genome):
    ''' Given a population of males and females, find a pair to breed.

    Args:
        females: all available females (removed by this method when returned)
        males: all available males (left in the list when returned)
        pool_size (int): how many alternatives to consider when finding the best 

    Returns:
        (Female, Male) to breed from
    
    '''
    n_females = len(females)
    n_males = len(males)

    best_match = -1       # the minimum possible is 0
    best_male = 0         # in practice this is always overridden

    # We assume that the females are the ones doing the selecting.
    female = females.pop(random.randint(0, n_females - 1))

    for _ in range(pool_size):
        pick = random.randint(0, n_males - 1)
        male = males[pick]
        male_matches = match(male.appearance, female.fancy)
        if not match:
            male_matches = NUMBER_OF_APPEARANCE_GENES - male_matches

        if male_matches > best_match:
            best_match = male_matches
            best_male = pick
    
    return (female, males[best_male])

def match(appearance: List[Gene], fancies: List[Gene]) -> int:
    '''Finds the quality of match between appearance and fancy genes
    '''
    # For now, we ignore the issue of dominant and regressive genes,
    # and just assume all genes are important. We assume that there
    # is a one-to-one mapping between appearance genes and the genes
    # to fancy that appearance.
    assert(len(appearance) == len(fancies))

    match = 0
    for appear, fancy in zip(appearance, fancies):
        appear_count = count_gene(appear)  # 0..2
        fancy_count = count_gene(fancy)    # 0..2
        diff = abs(appear_count - fancy_count)  # 0..2
        match += 2 - diff  # we want match to be greater if diff is small

    return match

def count_gene(gene: Gene) -> int:
    '''Counts the True genes in one pair.

    Returns:
        0 if both are Neanderthal. 2 if both are Sapiens
    '''
    count = 0
    if gene[0]:
        count += 1
    if gene[1]:
        count += 1
    return count

def reproductive(population: List[Genome], male: bool, cycle: int) -> List[Genome]:
    ''' Given a mixed population, find the females/males who can reproduce.

    Args:
        population: Males and females of any age. This list is not changed.
        male: If true, look for males. If false, look for females.
        cycle: The current breeding cycle. May be used to exclude individuals
            who are too young or old

    Returns:
        List of females or males who can reproduce
    '''
    result = []

    for individual in population:
        if individual.is_male == male:
            result.append(individual)
    
    return result

def count_genes(genes: List[Gene]) -> int:
    '''Counts both of each gene that matches
    '''
    total = 0
    for gene in genes:
        if gene[0]:
            total += 1
        if gene[1]:
            total += 1
    
    return total

def merge(male: List[Gene], female: List[Gene]) -> List[Gene]:
    '''Randomly merges two gene-lists, taking one gene from each
    '''

    result = []

    for male_gene, female_gene in zip(male, female):
        pick_male = male_gene[random.randint(0,1)]
        pick_female = female_gene[random.randint(0,1)]
        result.append((pick_male, pick_female))
    
    return result

def one_culling_cycle(population: List[Genome]):
    '''Kills off some proportion of the population.

    The population is in order, with oldest individuals first. Within
    this function, Monte-Carlo draws are taken and probabilities
    evaluated such that some individuals are removed from the
    population.

    Args:
        population: List of all individuals. Modified by this function.
    
    Returns:
        None: The input list is modified in situ.
    '''

    # Kill off males and females at random, rather than
    # worrying about age or gender population totals
    MAX_POPULATION = 2000
    while len(population) > MAX_POPULATION:
        n_population = len(population)
        pick = random.randint(0, n_population - 1)
        del population[pick]

def repeated_cycles(
    population: List[Genome], 
    pool_size: int, 
    max_cycles: int, 
    extra_cycles: int):
    ''' Repeatedly alternates breeding and culling cycles.

    The input lists are modified in situ.

    Args:
        population: All individuals. This list is modified by the function.
        pool_size (int): number of choices when picking a partner
        max_cycles (int): max number of repeated breeding and culling cycles
        extra_cycles (int): if we run out of neanderthal y-chromosomes, just
            run a few extra cycles to stabilise the population. Still
            limited by max_cycles

    Returns:
        int: The number of cycles actually performed

    '''

    # When we run out of neanderthal y-chromosomes, the population quickly
    # stabilises. Just run a few extra cycles to let this happen
    cycles_after_last_neaderthal = extra_cycles

    for cycle in range(max_cycles):
        one_breeding_cycle(population, cycle, pool_size)
        one_culling_cycle(population)

        # No point continuing long if there are no neanderthal y-chromosomes left.
        # The population stabilises very quickly
        if not any_male_neanderthals(population):
            cycles_after_last_neaderthal -= 1
            if cycles_after_last_neaderthal == 0:
                return cycle + 1
    
    return max_cycles

def any_male_neanderthals(population: List[Genome]) -> bool:
    ''' Returns true if there are any males with neanderthal Y-chromosomes

    Args:
        population:
    
    Returns:
        True if there are any neanderthal Y-chromosomes
    '''
    for individual in population:
        if individual.is_male and individual.is_neanderthal:
            return True
    
    return False

def print_stats(population: List[Genome], pool_size: int, cycles: int):
    '''Writes to stdout a comma-separated list of stats

    Args:
        population: List of all individuals
        pool_size (int): number of choices when picking a partner
        cycles (int): number of repeated breeding and culling cycles

    '''

    n_total = len(population)
    n_male = 0
    n_neander_y = 0

    total_appearance = 0.0
    total_fancy = 0.0
    total_miscarry = 0.0
    total_other = 0.0

    for individual in population:
        total_appearance += count_genes(individual.appearance)
        total_fancy += count_genes(individual.fancy)
        total_miscarry += count_genes(individual.miscarry)
        total_other += count_genes(individual.other)
        if individual.is_male:
            n_male += 1
            if individual.is_neanderthal:
                n_neander_y += 1

    mean_appearance = total_appearance / (n_total * NUMBER_OF_APPEARANCE_GENES * 2)
    mean_fancy = total_fancy / (n_total * NUMBER_OF_FANCY_GENES * 2)
    mean_miscarry = total_miscarry / (n_total * NUMBER_OF_MISCARRY_GENES * 2)
    mean_other = total_other / (n_total * NUMBER_OF_OTHER_GENES * 2)

    print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
        pool_size, cycles, n_total, n_male, n_neander_y,
        mean_appearance, mean_fancy, mean_miscarry, mean_other))

def print_header():
    ''' Writes to stdout a line of comma-separated column titles
    '''

    print("pool\tcycles\tpop\tmales\tneander_y\tappearance\tfancy\tmiscarry\tother")

# Simple test code, if the module is invoked directly from the command line.
# Evolve the population given a sensible starting point with equal populations
# of pure-bred neanderthals and sapiens, then print out the final state.   
if __name__ == '__main__':

    print_header()

    sapiens_gene = [Gene(True, True)]
    neanderthal_gene = [Gene(False, False)]
        
    male_sapiens = Genome(
        sapiens_gene * NUMBER_OF_APPEARANCE_GENES,
        sapiens_gene * NUMBER_OF_FANCY_GENES,
        sapiens_gene * NUMBER_OF_MISCARRY_GENES,
        sapiens_gene * NUMBER_OF_OTHER_GENES,
        True, False, -1)
    female_sapiens = Genome(
        sapiens_gene * NUMBER_OF_APPEARANCE_GENES,
        sapiens_gene * NUMBER_OF_FANCY_GENES,
        sapiens_gene * NUMBER_OF_MISCARRY_GENES,
        sapiens_gene * NUMBER_OF_OTHER_GENES,
        False, False, -1)
    male_neanderthal = Genome(
        neanderthal_gene * NUMBER_OF_APPEARANCE_GENES,
        neanderthal_gene * NUMBER_OF_FANCY_GENES,
        neanderthal_gene * NUMBER_OF_MISCARRY_GENES,
        neanderthal_gene * NUMBER_OF_OTHER_GENES,
        True, True, -1)
    female_neanderthal = Genome(
        neanderthal_gene * NUMBER_OF_APPEARANCE_GENES,
        neanderthal_gene * NUMBER_OF_FANCY_GENES,
        neanderthal_gene * NUMBER_OF_MISCARRY_GENES,
        neanderthal_gene * NUMBER_OF_OTHER_GENES,
        False, True, -1)

    for _ in range(10):   # repeated tests with different MonteCarlo draws   
        for pool_size in range(1, 5):    # repeat with different pool sizes

            population = [male_sapiens, female_neanderthal, male_neanderthal, female_sapiens] * 200
            cycles = repeated_cycles(population, pool_size, 400, 40)
            print_stats(population, pool_size, cycles)

 
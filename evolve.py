import random

def one_breeding_cycle(male_sapiens, male_neanders, females, pool_size):
    '''Executes one breeding cycle, given a population of mixed species

    Each of the population parameters is a list of floating point numbers,
    representing the genetic mix, where 0.0 is fully neanderthal and 1.0
    is fully sapiens. For example, an initial call to the function might pass
    arrays where male sapiens are all set to 1.0 and male neanderthal are all
    set to 0.0, and the females are a mix of 1.0 sapiens and 0.0 neanderthals.

    The definition of a neanderthal is someone who can successfully breed with
    another neanderthal, but when breeding with sapiens follows the following
    rule:

    male_sapiens + female(neanderthal) -> mixed species offspring
    male_neanderthal + female(sapiens) -> miscarriage if boy
    male_neanderthal + female(mixed) -> either miscarriage or mixed offspring

    In other words, the difference between male_sapiens and male_neanderthal is
    that the latter carries a neanderthal Y-chromosome. The probability of 
    miscarriage when a male foetus carries a neanderthal Y-chromosome is defined by the
    miscarry_with_neanderthal function, which is called from within this function.

    The probability of a sapiens mating with a neanderthal is defined by the 
    find_partner function, which is called from within this function.

    Args:
        male_sapiens (List[float]): males with sapiens y-chromosome
        male_neanders (List[float]): males with neanderthal y-chromosome
        females (List[float]): females of any species
        pool_size (int): how many partners to consider when finding the best  

    Returns:
        None: The input lists are all modified in place.

    '''

    # Create arrays for offspring. We assume these cannot mate within this cycle,
    # so keep them separate
    boy_sapiens = []
    boy_neanders = []
    girls = []

    # Each female tries to mate. We assume that all females mate with at most one
    # partner at a time, so we iterate through females rather than males. Males on
    # the other hand may have zero, one or many partners in any cycle. 
    for female in females:
        boy = random.randint(0, 1) == 0 # assume equal probability of boy or girl
        (is_sapiens, male) = find_partner(female, male_sapiens, male_neanders, pool_size)
        mix = (male + female) * 0.5
        if not boy:
            # girls never miscarry (at least in this simulation)
            girls.append(mix)
        if is_sapiens:
            # no miscarriages with sapiens Y-chromosome
            boy_sapiens.append(mix)
        elif not miscarry_with_neanderthal(female):
            # picked a neanderthal, produced a male foetus, and tested for miscarriage
            boy_neanders.append(mix)

    # Append the new individuals to the ends of the lists. We keep them
    # at the end, so position in the list is an indication of age. For
    # example, we may want to preferentially kill off older individuals.

    male_sapiens.extend(boy_sapiens)
    male_neanders.extend(boy_neanders)
    females.extend(girls)

    return None

def find_partner(female, male_sapiens, male_neanders, pool_size):
    ''' Finds a male partner for the given female.

    The female's species is a floating point number ranging from 0.0
    meaning totally neanderthal to 1.0 meaning totally sapiens. The
    populations of male sapiens and neanders are both lists of floats,
    with the same meaning.

    Args:
        female (float): the sapiensness of the female
        male_sapiens (List[float]): males with sapiens y-chromosome
        male_neanders (List[float]): males with neanderthal y-chromosome
        pool_size (int): how many males to consider when finding the best 

    Returns:
        (bool, float): The bool is true if the male partner has a sapiens
            y-chromosome. The float represents the sapiensness of the partner.
    
    '''
    n_sapiens = len(male_sapiens)
    n_neanders = len(male_neanders)
    n_total = n_sapiens + n_neanders

    # We assume that the genes for fancying sapiens generally go with sapiens
    # genes and vice versa. To generalise, we try to minimize the genetic distance
    # (L_inf norm) between the male and female. We take a number of draws and pick
    # the best. The number of draws makes a critical difference to the outcome.

    best_distance = 1.1      # the maximum possible is 1
    best_male = 0.0          # in practice this is always overridden
    best_is_sapiens = False  # this is also overridden

    # experimentally adjust the female, pushing her to one or other extreme
    adj_female = 0.0 if female < 0.5 else 1.0

    for _ in range(pool_size):
        pick = random.randint(0, n_total - 1)
        is_sapiens = pick < n_sapiens
        if is_sapiens:
            male = male_sapiens[pick]
        else:
            male = male_neanders[pick - n_sapiens]

        distance = abs(male - adj_female)   # L infinite norm
        if distance < best_distance:
            best_distance = distance
            best_male = male
            best_is_sapiens = is_sapiens
    
    assert(best_distance <= 1.0)
    return (best_is_sapiens, best_male)

def miscarry_with_neanderthal(female):
    '''Will sex between a neanderthal male and the given female result in
    miscarriage?

    Assumes that the foetus is male and carries the neanderthal Y-chromosome.

    We make the simplifying assumption that the miscarriage-causing genes are
    equally spread among all genes, so whether a miscarriage occurs is a
    probabilistic function of the proportion of sapiens-ness, with 100% probability
    for sapiens and 0% probability for neanderthal. The shape of the function, and
    the Monte-Carlo draws that define instances are internal to this function.

    Args:
        female (float): The sapiensness of the female carrying the foetus

    Returns:
        bool: true if there is miscarriage, or false if the pregnancy runs to term.

    '''

    # For simplicity, assume a linear probabilistic function, where a neanderthal
    # female (0.0) has zero probability of miscarrying and a sapiens female (1.0)
    # miscarries with probability one.
    draw = random.random()  # a uniform draw between zero and one: range [0, 1)
    return draw < female    # always true if female = 1.0, never true if female = 0.0

def one_culling_cycle(male_sapiens, male_neanders, females):
    '''Kills off some proportion of the population.

    The parameters each list a number of individuals who may be
    neanderthal, sapiens or mixed race, represented by a floating
    point number which is 0.0 for neanderthal and 1.0 for sapiens.

    The only difference between male_sapiens and male_neanders is
    the Y chromosome, which here we assume has no impact on
    survival.

    The lists are in order, with oldest individuals first. Within
    this function, Monte-Carlo draws are taken and probabilities
    evaluated such that some individuals are removed from the
    population.

    Args:
        male_sapiens (List[float]): males with sapiens y-chromosome
        male_neanders (List[float]): males with neanderthal y-chromosome
        females (List[float]): females of any species

    Returns:
        None: The input lists are modified in situ.
    '''

    # For now, we keep things really simple, and just keep the total
    # males and females to some maximum, by killing the oldest. We also
    # kill some fixed number each year from each population, just to avoid
    # steady state solutions where nobody ever dies.
    MALE_MAX_POPULATION = 10000
    FEMALE_MAX_POPULATION = 10000
    ALWAYS_KILL = 10

    n_sapiens = len(male_sapiens)
    n_neanders = len(male_neanders)
    n_males = n_sapiens + n_neanders

    # Kill excess old women
    n_females = len(females)
    kill_females = max(n_females - FEMALE_MAX_POPULATION - ALWAYS_KILL, 0) + ALWAYS_KILL
    del females[0:kill_females]

    # Kill excess old men. We have to be careful here, because we
    # want to equally kill neanderthals and sapiens according to
    # the proportions in their populations. (Not totally sure this
    # is fair, as the ages may be different.)
    kill = max(n_males - MALE_MAX_POPULATION - ALWAYS_KILL, 0)
    kill_neanders = (kill * n_neanders) // n_males + ALWAYS_KILL
    kill_sapiens = (kill * n_sapiens) // n_males + ALWAYS_KILL
    del male_neanders[0:kill_neanders]
    del male_sapiens[0:kill_sapiens]

def repeated_cycles(male_sapiens, male_neanders, females, pool_size, max_cycles, extra_cycles):
    ''' Repeatedly alternates breeding and culling cycles.

    The input lists are modified in situ.

    Args:
        male_sapiens (List[float]): males with sapiens y-chromosome
        male_neanders (List[float]): males with neanderthal y-chromosome
        females (List[float]): females of any species
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
        one_breeding_cycle(male_sapiens, male_neanders, females, pool_size)
        one_culling_cycle(male_sapiens, male_neanders, females)

        # No point continuing long if there are no neanderthal y-chromosomes left.
        # The population stabilises very quickly
        if len(male_neanders) == 0:
            cycles_after_last_neaderthal -= 1
            if cycles_after_last_neaderthal == 0:
                return cycle + 1
    
    return max_cycles

def print_stats(male_sapiens, male_neanders, females, pool_size, cycles):
    '''Writes to stdout a comma-separated list of stats

    Args:
        male_sapiens (List[float]): males with sapiens y-chromosome
        male_neanders (List[float]): males with neanderthal y-chromosome
        females (List[float]): females of any species
        pool_size (int): number of choices when picking a partner
        cycles (int): number of repeated breeding and culling cycles

    '''
    
    n_sapiens = len(male_sapiens)
    n_neander = len(male_neanders)
    n_female = len(females)

    mean_sapiens = sum(male_sapiens) / n_sapiens if n_sapiens > 0 else 0
    mean_neander = sum(male_neanders) / n_neander if n_neander > 0 else 0
    mean_female = sum(females) / len(females) if n_female > 0 else 0

    print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
        pool_size, cycles,
        n_sapiens, mean_sapiens, 
        n_neander, mean_neander,
        n_female, mean_female))

def print_header():
    ''' Writes to stdout a line of comma-separated column titles
    '''

    print("pool\tcycles\tsapiens\tmean-sapiens\tneanders\tmean-neander\tfemales\tmean-female")

# Simple test code, if the module is invoked directly from the command line.
# Evolve the population given a sensible starting point with equal populations
# of pure-bred neanderthals and sapiens, then print out the final state.   
if __name__ == '__main__':

    print_header()

    for _ in range(10):   # repeated tests with different MonteCarlo draws   
        for pool_size in range(1, 7):    # repeat with different pool sizes

            male_sapiens = [1.0] * 2000
            male_neanders = [0.0] * 2000
            females = [1.0, 0.0] * 2000
            cycles = repeated_cycles(male_sapiens, male_neanders, females, pool_size, 400, 40)
            print_stats(male_sapiens, male_neanders, females, pool_size, cycles)

 
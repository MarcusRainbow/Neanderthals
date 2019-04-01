import random

def one_breeding_cycle(male_sapiens, male_neanders, females):
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
    male_neanderthal + female(sapiens) -> miscarriage
    male_neanderthal + female(mixed) -> either miscarriage or mixed offspring

    Mixed race offspring are always classed as sapiens if they are male. (They
    have a sapiens Y chromosome.) If they are female, they may be sapiens or
    neanderthal, depending on whether they would miscarry if mating with a
    neanderthal male. This depends on multiple genes carried by both female and
    male. The probability of miscarriage is defined by the
    miscarry_with_neanderthal function, which is called from within this function.

    The probability of a sapiens mating with a neanderthal is defined by the 
    find_partner function, which is called from within this function.

    Returns None. The input lists are all modified in place.

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
        (is_sapiens, male) = find_partner(female, male_sapiens, male_neanders)
        mix = (male + female) * 0.5
        if is_sapiens:
            # picked a sapiens. No chance of miscarriage, so easy
            if boy:
                boy_sapiens.append(mix)
            else:
                girls.append(mix)
        elif not miscarry_with_neanderthal(female):
            # picked a neanderthal, and tested for miscarriage
            if boy:
                boy_neanders.append(mix)
            else:
                girls.append(mix)

    # Append the new individuals to the ends of the lists. We keep them
    # at the end, so position in the list is an indication of age. For
    # example, we may want to preferentially kill off older individuals.

    male_sapiens.extend(boy_sapiens)
    male_neanders.extend(boy_neanders)
    females.extend(girls)

    return None

def find_partner(female, male_sapiens, male_neanders):
    ''' Finds a male partner for the given female.

    The female's species is a floating point number ranging from 0.0
    meaning totally neanderthal to 1.0 meaning totally sapiens. The
    populations of male sapiens and neanders are both lists of floats,
    with the same meaning.

    Returns a tuple of a boolean (true if sapiens) and a floating point
    number representing the sapiens-ness of the partner.
    '''
    n_sapiens = len(male_sapiens)
    n_neanders = len(male_neanders)
    n_total = n_sapiens + n_neanders

    # We assume that the genes for fancying sapiens generally go with sapiens
    # genes and vice versa. To generalise, we try to minimize the genetic distance
    # (L_inf norm) between the male and female. We take a number of draws and pick
    # the best. The number of draws makes a critical difference to the outcome.

    NUMBER_OF_DRAWS = 4

    best_distance = 1.1      # the maximum possible is 1
    best_male = 0.0          # in practice this is always overridden
    best_is_sapiens = False  # this is also overridden

    for _ in range(NUMBER_OF_DRAWS):
        pick = random.randint(0, n_total - 1)
        is_sapiens = pick < n_sapiens
        if is_sapiens:
            male = male_sapiens[pick]
        else:
            male = male_neanders[pick - n_sapiens]

        distance = abs(male - female)   # L infinite norm
        if distance < best_distance:
            best_distance = distance
            best_male = male
            best_is_sapiens = is_sapiens
    
    assert(best_distance <= 1.0)
    return (best_is_sapiens, best_male)

def miscarry_with_neanderthal(female):
    '''Will sex between a neanderthal male and the given female result in
    miscarriage?

    We make the simplifying assumption that the miscarriage-causing genes are
    equally spread among all genes, so whether a miscarriage occurs is a
    probabilistic function of the proportion of sapiens-ness, with 100% probability
    for sapiens and 0% probability for neanderthal. The shape of the function, and
    the Monte-Carlo draws that define instances are internal to this function.

    Returns true if there is miscarriage, or false if the pregnancy runs to term.
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

    Returns None. The input lists are modified in situ.
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
    kill_females = max(n_females - FEMALE_MAX_POPULATION, 0) + ALWAYS_KILL
    del females[0:kill_females]

    # Kill excess old men. We have to be careful here, because we
    # want to equally kill neanderthals and sapiens according to
    # the proportions in their populations. (Not totally sure this
    # is fair, as the ages may be different.)
    kill = max(n_males - MALE_MAX_POPULATION, 0)
    kill_neanders = (kill * n_neanders) // n_males + ALWAYS_KILL
    kill_sapiens = (kill * n_sapiens) // n_males + ALWAYS_KILL
    del male_neanders[0:kill_neanders]
    del male_sapiens[0:kill_sapiens]

def repeated_cycles(male_sapiens, male_neanders, females, cycles):
    ''' Repeatedly alternates breeding and culling cycles for the given
    number of cycles.

    '''

    for _ in range(cycles):
        one_breeding_cycle(male_sapiens, male_neanders, females)
        one_culling_cycle(male_sapiens, male_neanders, females)

# Simple test code, if the module is invoked directly from the command line.
# Evolve the population given a sensible starting point with equal populations
# of pure-bred neanderthals and sapiens, then print out the final state.   
if __name__ == '__main__':
    male_sapiens = [1.0] * 1000
    male_neanders = [0.0] * 1000
    females = [1.0, 0.0] * 1000
    repeated_cycles(male_sapiens, male_neanders, females, 100)

    mean_male_sapiens = sum(male_sapiens) / len(male_sapiens)
    if len(male_neanders) > 0:
        mean_male_neander = sum(male_neanders) / len(male_neanders)
    else:
        mean_male_neander = 0.0
    mean_female = sum(females) / len(females)

    print("male_sapiens: number={} mean={}", len(male_sapiens), mean_male_sapiens)
    print("male_neander: number={} mean={}", len(male_neanders), mean_male_neander)
    print("female: number={} mean={}", len(females), mean_female)

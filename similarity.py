import math


# Constants from original paper:
K1 = 0.348

# weights for intervals out of scale
TON = {
	0: 0.6,
	1: 2.6,
	2: 2.3,
	3: 1,
	4: 1,
	5: 1.6,
	6: 1.8,
	7: 0.8,
	8: 1.3,
	9: 1.3,
	10: 2.2,
	11: 2.5
}

MINOR_DEG: {
	1: 1,
	3: 2,
	4: 3,
	6: 4,
	8: 5,
	9: 6,
	12: 7
}

MAJOR_DEG: {
	1: 1,
	3: 2,
	5: 3,
	6: 4,
	8: 5,
	10: 6,
	12: 7
}

DEG_DIFF = {
	0: 0,
	1: 0.9,
	2: 0.2,
	3: 0.5,
	4: 0.1,
	5: 0.35,
	6: 0.8
}

REST = 0.1

MU = 2

D = 0.6

def w_ins():
	pass


def w_del():
	pass


def w_frag(): 
	pass


def w_cons():
	pass


def w_interval():
	pass


def w_len():
	pass


'''
:param a: A list of notes of (pitch, duration)
:param b: A list of notes of (pitch, duration)
:return: Calculated distance
'''
def ms_distance(a, b):

	# Ends of recursion:

	if len(a) == 0 or len(b) == 0:
		return 0;

	distance_matrix = []

	for i, _ in enumerate(a):
		if i > 0:
			distance_matrix.append([matrix[i-1] + w_del(a, i))
		else:
			distance_matrix.append([i])

	for i, _ in enumerate(b):
		if i > 0:
			distance_matrix[0][i] = [matrix[0][i-1] + w_ins(b, i)
		else:
			distance_matrix[0][i] = i

	# Constants for dynamic programming
	max_duration_a = 0;
    min_duration_b = math.inf;
    for note in a:
        if max_duration_a < note.duration:
            max_duration_a = note.duration
    for note in b:
        if min_duration_b > note.duration:
            min_duration_b = note.duration


    F = math.ceil(max_duration_a / min_duration_b)

    max_duration_b = 0;
    min_duration_a = math.inf;
    for note in b:
        if max_duration_b < note.duration:
            max_duration_b = note.duration
    for note in a:
        if min_duration_a > note.duration:
            min_duration_a = note.duration


    C = math.ceil(max_duration_b / min_duration_a)

    ## Filling the rest of matrix


## Determine by the name of folder, wheter to use major or minor degrees


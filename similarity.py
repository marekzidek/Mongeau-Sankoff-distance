# This code is a mongeau-sankoff measure improved by adding polyphony and analyzing
# multiple tracks for self-analysis.
#TODO: after addition of retrograd and inverse intervals, add it to this annotation
# The baseline of it is inspired by freakimkaefig/musicjson-toolbox on github, 
# adding a minor mode to it and rewriting it to python with some tweaks


import math
import midi

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

MINOR_DEG = {
	0: 1,
	2: 2,
	3: 3,
	5: 4,
	7: 5,
	8: 6,
	11: 7
}

MAJOR_DEG = {
	0: 1,
	2: 2,
	4: 3,
	5: 4,
	7: 5,
	9: 6,
	11: 7
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

def w_ins(note_b):
	return K1 * note_b.duration


def w_del(note_a):
	return K1 * note_a.duration


def w_sub(note_a, note_b):
	return w_interval(note_a, note_b) + K1 * w_len(note_a.duration, note_b.duration)


def w_frag(distance_matrix, a, b, i, j, F):
	min_weight = math.inf
	
	for x in range(2, math.min(j, F)):
		
		k = x

		weight = distance_matrix[i-1][j-k]
		durations = 0
		
		while k > 0:
			weight += w_interval(a[i-1], b[j-k])
			durations += b[j-k].duration
			k -= 1
		
		weight += K1 * w_len(a[i-1.duration, durations])

		if min_weight > weight:
			min_weight = weight

	return min_weight


def w_cons(distance_matrix, a, b, i, j, C):
	min_weight = math.inf

	for x in range(2, math.min(i, C)):

		k = x

		weight = distance_matrix[i-k][j-1]
		durations = 0

		while k > 0:
			weight += w_interval(a[i-k], b[j-1])
			durations += a[i-k].duration
			k -= 1
		
		weight += K1 * w_len(durations, b[j-1].duration)

	if min_weight > weight:
			min_weight = weight

	return min_weight



def w_interval(note_a, note_b):
	if note_a.rest or note_b.rest:
		if note_a.rest and note_b.rest:
			return DEG_DIFF[0]
		return REST

	# Given that we represent notes as modulo to tonic
	if note_a.scale == major:
		degree_a = MAJOR_DEG[note_a.value]
		debree_b = MAJOR_DEG[note_b.value]
	elif note_b.scale == minor:
		degree_a = MINOR_DEG[note_a.value]
		degree_b = MINOR_DEG[note_b.value]
	else:
		return TON[math.abs(note_a.value - note_b.value)]

	return DEG_DIFF[math.abs(degree_a - degree_b)]
	

# Takes durations
def w_len(note_a, note_b):
	return math.abs(note_a - note_b)



class Note:
	__init__(self, value, rest, duration, scale):
		self.value = value
		self.rest = rest
		self.duration = duration
		self.scale = scale

'''

'''
def midi2notes(midifile):
#TODO: encode them as a difference from the tonic

'''
Notes are objects of : .value, .rest, .duration, .poly
#TODO: we could possibly omit the poly and have .value and .duration be lists of max length like 3 or 4 max polyphony within track
'''


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

	for i in range(len(a) + 1):
		if i > 0:
			distance_matrix.append([matrix[i-1] + w_del(a, i))
		else:
			distance_matrix.append([i])

	for i  in range(len(b) + 1):
		if i > 0:
			distance_matrix[0].append([matrix[0][i-1] + w_ins(b, i))
		else:
			distance_matrix[0].append([i])

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

    for i, note_a in enumerate(a,0):
    	for j, note_b in enumerate(b,0):
    		#TODO: here, lets make it work with the value polyhony array, yeah -> make it ugly
    		if a[i].value == b[j].value and a[i].rest == b[j].rest and a[i].duration == b[j].duration:
    			distance_matrix[i+1][j+1] = distance_matrix[i][j]
    		else:
    			deletion = distance_matrix[i][j + 1] + w_del(note_a)
    			insertion = distance_matrix[i + 1][j] + w_ins(note_b)
    			substitution = distance_matrix[i][j] + w_sub(note_a, note_b)
    			fragmentation = w_frag(distance_matrix, a, b, i + 1, j + 1, F)
    			consolidation = w_cons(distance_matrix, a, b, i + 1, j + 1, C)

    			distance_matrix[i+1][j+1] = min(deletion, insertion, substitution, fragmentation, consolidation)

	#TODO: for further improvements, we could do a max rescaling here as they do in musicjson-toolbox
    return distance_matrix[len(a)+1][len(b)+1]





## Determine by the name of folder, wheter to use major or minor degrees


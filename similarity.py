


# Constants from original paper:
K1 = 0.348

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

DEG = {
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

	if len(a) == 0 or len(b) == 0:
		retunr 0;

	distance_matrix = []

	for i, _ in enumerate(a):
		if i > 0:
			distance_matrix[i] = [matrix[i-1] + W_A_NULL] 



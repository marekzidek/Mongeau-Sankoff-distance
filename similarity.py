# This code is a mongeau-sankoff measure improved by adding polyphony and analyzing
# multiple tracks for self-analysis.
#TODO: after addition of retrograd and inverse intervals, add it to this annotation
# The baseline of it is inspired by freakimkaefig/musicjson-toolbox on github, 
# adding a minor mode to it and rewriting it to python with some tweaks

import instrument_classes

import math
import midi
from enum import Enum

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
		degree_a = MAJOR_DEG[note_a.pitch % 12]
		debree_b = MAJOR_DEG[note_b.pitch % 12]
	elif note_b.scale == minor:
		degree_a = MINOR_DEG[(note_a.pitch + 9) % 12]
		degree_b = MINOR_DEG[(note_b.pitch + 9) % 12]
	else:
		return TON[math.abs(note_a.pitch - note_b.pitch)]

	return DEG_DIFF[math.abs(degree_a - degree_b)]
	

# Takes durations
def w_len(note_a, note_b):
	return math.abs(note_a - note_b)


class Note(Object):
	__init__(self, pitch, rest, duration, scale):
		self.pitch = pitch
		self.rest = rest
		self.duration = duration
		self.scale = scale

		# Indicates when to look for meter changes
		self.meter_change = False

class Meter_change(Enum):
	TRUE
	FALSE

'''
Scale should be determined just by being in a specified folder (by preprocessing transpose to C/A)
That is major/minor/atonal
Returns: 
	tracks of notes(pitch, rest, duration, scale) and meter change events for each channel,
 	instruments for each channel,
	list of meters (change times are encoded in tracks (first returned value))
'''
def midi2notes(midifile, scale):

	# these dict of list of dicts that is:
	# dict for each channel, list for each event, dict for {pitch; rest, duration}
	note_ons = dict()
	rests = dict()
	tracks = dict()

	instruments = dict()
	meter = []

	pattern = midi.read_midifile(midifile)

	remaining_time = [track[0].ticks for track in pattern]
	position_in_track = [0 for track in pattern]
	
	while not (all(t is None for t in remaining_time)):
		
		# new sixteenth step
		if currTime % (pattern.resolution / 4) == (pattern.resolution / 8):

			for track_note_ons in note_ons:
				
				# Add rest if no held notes found
				if len(note_ons[track_note_ons]) == 0:
					note_ons[track_note_ons].append({"pitch":-1, "rest":True, "len":1})

				# Prolong everything by 1 sixteenth
				for notes in note_ons[track_note_ons]:
					notes["len"] += 1
				


		for i in range(len(remaining_time)):

			while remaining_time[i] == 0:

				track = pattern[i]
				pos = position_in_track[i]

				event = track[pos]

				if isinstance(event, midi.ProgramChangeEvent):
					if i not in tracks:
						# tracks hold pitch, rest, duration, scale for each note
						tracks[i] = []
						note_ons[i] = []
						instruments[i] = instrument_classes.get_instrument_class(event.data[0])
				
				if isinstance(event, midi.TimeSignatureEvent):
					meter.append(event.nominator + "/" + event.denominator)

					for i in tracks:
						tracks[i].append(Meter_Change.TRUE)
				
				if isinstance(event, midi.NoteEvent):

					if isinstance(event, midi.NoteOffEvent) or event.velocity == 0:
						for note in note_ons[i]:
							if note["pitch"] == event.pitch:
								new_note = Note(pitch=note["pitch"], rest=False, duration=note["len"], scale=scale)
								tracks[i].append(new_note)
								note_ons[i].remove(note)

								if note in note_ons[i]:
									print("DEBUG: Je hlaseno nebezpeci mili agenti 007")
					else:
						#TODO: detect ongoing notes for new polyphonies

						# Delete rests
						for rest in note_ons[i]:
							if rest["rest"]:
								new_note = Note(pitch=-1, rest=True, duration=rest["len"], scale=scale)
								tracks[i].append(new_note)
								note_ons[i].remove(rest)

								if rest in note_ons[i]:
									print("DEBUG: Je hlaseno nebezpeci mili agenti 007")

						note_ons[i].append({"pitch":event.pitch, "rest":False, "len":0})
				try:
                    remainingTime[i] = track[pos + 1].tick
                    positionInTrack[i] += 1
                    
                # a bit of a bad practice here, but it's not the main time consuming part of the program
                except IndexError:
                    remainingTime[i] = None

            if remainingTime[i] is not None:
                remainingTime[i] -= 1

        if all(t is None for t in remainingTime):
            break

        currTime += 1

	
	return tracks, instruments, meter




	get_instrument_class() 


	return # append all to one sequence or just update it to run in on more sequences

'''
Notes are objects of : .pitch, .rest, .duration, .poly
#TODO: we could possibly omit the poly and have .pitch and .duration be lists of max length like 3 or 4 max polyphony within track
'''


'''
:param a: A list of notes of (pitch, rest, duration)
:param b: A list of notes of (pitch, rest, duration)
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


    F = int(math.ceil(max_duration_a / min_duration_b))

    max_duration_b = 0;
    min_duration_a = math.inf;
    for note in b:
        if max_duration_b < note.duration:
            max_duration_b = note.duration
    for note in a:
        if min_duration_a > note.duration:
            min_duration_a = note.duration


    C = int(math.ceil(max_duration_b / min_duration_a))

    ## Filling the rest of matrix

    for i, note_a in enumerate(a,0):
    	for j, note_b in enumerate(b,0):
    		#TODO: here, lets make it work with the pitch polyhony array, yeah -> make it ugly
    		if a[i].pitch == b[j].pitch and a[i].rest == b[j].rest and a[i].duration == b[j].duration:
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


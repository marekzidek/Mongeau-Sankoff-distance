import math

#NOTE: If anything seems wrong, just use data - 1, because midi-inventors decided to index from one :D
# but I am aware that somewhere between the versions and libraries, they could get some common sense 


# Our use case is obviously not using synth or some sound effects listed, but why not put them here :D
family_table = ["Piano", "Chromatic Percussion",
                "Organ", "Guitar", "Bass", "Strings", "Ensemble", "Brass",
                "Reed", "Pipe", "Synth Lead", "Synth Pad", "Synth Effects", 
                "Ethinc", "Percussive", "Sound Effects"]

# some instruments defined more softly -> choosing according to our use case (classical music)
soft_family_table = {
    41: "Violin",
    42: "Viola",
    43: "Cello",
    44: "Contrabass",
    65: "Higher Sax",
    66: "Higher Sax",
    68: "Lower Sax",
    69: "Lower Sax",
    110: "Bagpipe",
    113: "Tinkle Bell",
    115: "Steel Drums",
    120: "Reverse Cymbal"
}

def get_instrument_class(data):

    # midi-inventors counted from 1, other people from 0 so
    data = data + 1
    if data in soft_family_table:
        family = soft_family_table[data]

    else:
        try:
            family =  family_table[int(math.ceil(data / 8))]
        except:
            family = "Undefined"
    
    return family

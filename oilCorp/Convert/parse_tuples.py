# Parses returned tuples by the database into a single list
# Input: the database tuples
# Output: the list of values
def Parse_Tuples(tuples):
    id_list = []
    for index in range(0,17):
        id_list.append(tuples[index])
    return id_list

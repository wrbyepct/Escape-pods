
def Path():
    P = []
    for i in range(50):
        room = [100 if i != j else 0 for j in range(50)]
        P.append(room)
    return P


entrances = [24]
exits = [0, 49]
path = Path()




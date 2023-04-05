from operator import add
from time import sleep
from Path_5 import path, entrances, exits

"""
Method: 
    Start from entrances and push bunnies the whatever neighbors as mush as it could 
Would fail:
    1. Because there are rooms that directly connects to exits 
       and they ARE the rooms you want to push to full capacity 
       NOT any random rooms 
    2. If you start from entrance, there's no way you can tell which number of bunnies you should give to the next
       in order to optimize the numbers 


Better:
    Start the exits, and "ask" the rooms that are directly responsible for them
    then from there, those rooms would try their best to ask the maximum number for you 
"""


# Create supply record from entrances
def CombineEntrance(ent, pa):
    rooms = pa[ent[0]]
    for i in range(1, len(ent)):
        rooms = list(map(add, rooms, pa[ent[i]]))
    return rooms


def find_neighbors(rn, ac):
    global room_size
    global candidates
    neighbors = []
    for n in candidates:
        if path[n][rn] > 0 and n not in ac:
            neighbors.append(n)
    return neighbors


# Give the list of suppliers room numbers
def get_suppliers():
    global supplier_record
    global total_escape
    s = []
    for r in range(room_size):
        if supplier_record[r] > 0:
            if r in exits:
                # If supply directly go to exits, add it to total escape
                total_escape += supplier_record[r]
            else:
                s.append(r)
    return s


def give_supply(s, amount):
    global supplier_record
    s_has = supplier_record[s]
    # Calculate how much can give
    can_give = s_has if s_has <= amount else amount
    # Update supply record

    return can_give


def update_record(r, amount):
    global supplier_record
    global suppliers
    supplier_record[r] -= amount
    if supplier_record[r] == 0:
        # Remove the room if he has exhaust his supply
        suppliers.remove(r)


def get_ask_amount(r):
    ask_amount = 0
    for e in exits:
        if path[r][e] > 0:
            ask_amount += path[r][e]
    return ask_amount


def Ask_Supply(rn, amount, ac):
    can_give = 0
    if rn in suppliers:
        can_give = give_supply(rn, amount)
        update_record(rn, can_give)
        amount -= can_give

    # Check if it has neighbors to ask
    neighbors = find_neighbors(rn, ac)

    for n in neighbors:
        if amount == 0:
            return can_give
        n_could_give = path[n][rn]
        can_ask = n_could_give if n_could_give <= amount else amount
        ac_copy = ac.copy()
        ac_copy.append(n)
        n_collected = Ask_Supply(n, can_ask, ac_copy)
        if n_collected == 0:
            # If what I asked is zero from this neighbor, then I also won't be able to ask him anything
            path[n][rn] = 0
        else:
            can_give += n_collected
            # Update tunnel capacity
            amount -= n_collected
            path[n][rn] -= n_collected
    return can_give


room_size = len(path)
total_escape = 0
supplier_record = CombineEntrance(entrances, path)
suppliers = get_suppliers()
candidates = [r for r in range(room_size) if r not in exits and r not in entrances] # Any room that's NOT the exit or the entrance


# Find the asker(the room that directly connects to the exits) and the ask amount(how much it should send to the exits)
def main():
    global total_escape
    global candidates
    for room in candidates:
        ask_amount = get_ask_amount(room)
        if ask_amount != 0:
            asker = room
            asker_chain = [asker]
            collected = Ask_Supply(asker, ask_amount, asker_chain)
            # print(f"I'm asker {asker}, here is what I collected: {collected}")
            total_escape += collected


main()
print(total_escape)

from collections import defaultdict
from Path_1 import entrances, exits, path

SupplyRecords = defaultdict(int)


def solution(Start, End, Path):
    Rooms = len(Path[0])

    IntermediateRooms = list(filter(lambda n: n not in End and n not in Start, range(Rooms)))

    build_supply_records(Start, Rooms, Path)

    return ExitRooms(End, IntermediateRooms, Path)


def ExitRooms(exit_rooms, IntermediateRooms, Path):
    DSA = 0
    for rx in exit_rooms:
        DSA += SupplyRecords[rx]
    print(f"Direct supply from entrance: {DSA}")

    IPs = []
    for rx in exit_rooms:
        IPs += GetIntermediateProviders(rx, IPs, IntermediateRooms, Path)
    print(f"Rooms directly to exits: {IPs}\n")

    total = 0
    for rx in IPs:
        ask = 0
        for er in exit_rooms:
            ask += Path[rx][er]
        total += AskOneInIPs(rx, ask, Path, IntermediateRooms)
        print(f"Now number of {total} in the exits\n")

    return total + DSA


def build_supply_records(Start, Rooms, Path):
    amount_of_rooms = Rooms
    for i in Start:
        for j in range(amount_of_rooms):
            if Path[i][j] > 0:
                SupplyRecords[j] += Path[i][j]


def GetIntermediateProviders(Rx, IPs, IntermediateRooms, Path):
    intermediate_providers = IPs
    room_to_add = []

    for i in IntermediateRooms:
        if Path[i][Rx] > 0 and i not in intermediate_providers:
            room_to_add.append(i)
    return room_to_add


def AskOneInIPs(Rx, asked, Path, IntermediateRooms):
    print(f"We are now in Room {Rx}.")
    print(f"Asking Room {Rx} for {asked}")

    # Directly supply amount
    DSA = SupplyRecords[Rx]
    print(f"Direct supply amount from entrances to Room {Rx}: {DSA}")

    # The amount that currently can give
    cur_canGive = DSA if DSA <= asked else asked
    print(f"Room {Rx} currently can give: {cur_canGive}")

    # If the room has direct supply, take at maximum of asked amount and update the record
    if DSA > 0:
        SupplyRecords[Rx] -= cur_canGive
        print(f"Updated SupplyRecords: {SupplyRecords}")

    # If the direct supply has already satisfied the asked amount,
    if cur_canGive == asked:
        print(f"Room {Rx} totally can give: {cur_canGive}")
        return cur_canGive
    IPs = []
    IPs = GetIntermediateProviders(Rx, IPs, IntermediateRooms, Path)

    print(f"Intermediate Providers: {IPs}")

    # If the room doesn't have intermediate providers, and don't have direct supply
    if not IPs and DSA == 0:
        print(f"Request failed because supply cannot travel to Room {Rx}.")
        print(f"Room {Rx} totally can give: {0}")
        return 0

    # If the room doesn't have intermediate providers but do have direct supply
    if not IPs:
        print(f"Room {Rx} totally can give: {cur_canGive}")
        return cur_canGive

    # Loop through all IPs
    for rx in IPs:
        # If at this point still_need == 0, no need to ask another intermediate room
        still_need = asked - cur_canGive if (asked - cur_canGive) > 0 else 0
        print(f"Room {Rx} still needs: {still_need}")
        if still_need == 0:
            print(f"Room {Rx} totally can give: {cur_canGive}\n")
            return cur_canGive
        print(f"Checking quota from Room {rx} to Room {Rx}: {Path[rx][Rx]}\n")
        if Path[rx][Rx] != 0:
            allow_by_rx = Path[rx][Rx]
            ask_amount = still_need if still_need <= allow_by_rx else allow_by_rx
            print(f"Asking for Room {rx}...")

            successfully_asked = AskOneInIPs(rx, ask_amount, Path, IntermediateRooms)
            cur_canGive += successfully_asked
            # Update quota of  Room x to Room X
            Path[rx][Rx] -= successfully_asked
            print(f"The quota Room {rx} to Room {Rx} is now: {Path[rx][Rx]}")
    print(f"Room {Rx} totally can give: {cur_canGive}\n")
    return cur_canGive


print(solution(entrances, exits, path))

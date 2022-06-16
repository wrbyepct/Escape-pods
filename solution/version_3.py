from collections import defaultdict
from Path_1 import entrances, exits, path

SupplyRecords = defaultdict(int)


def solution(Start, End, Path):

    def build_supply_records():
        """
        Build the dict that track the supply amount to the specific rooms
        (i.e. SR[2] == 15 means the total supply go to Room 2 from entrances is 15 )
        """
        amount_of_rooms = Rooms
        for i in Start:
            for j in range(amount_of_rooms):
                if Path[i][j] > 0:
                    SupplyRecords[j] += Path[i][j]

    class Room:
        @staticmethod
        def get_intermediate_providers(Rx):
            """
            Returns the rooms directly connected to the target room which still have quota
            """
            room_to_add = []
            for i in IntermediateRooms:
                if Path[i][Rx] > 0:
                    room_to_add.append(i)
            return room_to_add

        @staticmethod
        def Ask(Rx, asked):
            print(f"We are now in Room {Rx.name}.")
            print(f"Asking Room {Rx.name} for {asked}")

            # It means the asked amount == currently can give
            if not Rx.DPs:
                print(f"Room {Rx.name} totally can give: {Rx.cur_canGive}")
                return Rx.cur_canGive

            print(f"The direct providers of Room {Rx.name} are: {Rx.DPs}")
            for rx in Rx.DPs:
                still_need = Rx.still_need(asked)
                print(f"Room {Rx.name} still needs: {still_need}\n")
                if still_need == 0:
                    return Rx.cur_canGive
                allow_by_rx = Path[rx][Rx.name]
                Rx.ask_one_in_DPs(rx, allow_by_rx, still_need)
                print(f"The quota from Room {rx} to {Rx.name} is: {allow_by_rx}")

            print(f"Room {Rx.name} has now gathered: {Rx.cur_canGive}\n")
            return Rx.cur_canGive

    class Requesters(Room):
        exit_rooms = End

        def __init__(self):
            self.DSA = self.get_DSA()
            self.IPs = self.get_IPs()
            self.total = self.get_from_providers(self.IPs) + self.DSA

        @classmethod
        def get_DSA(cls):
            DSA = 0
            for rx in cls.exit_rooms:
                DSA += SupplyRecords[rx]
            print(f"Direct supply from entrance: {DSA}")
            return DSA

        @classmethod
        def get_IPs(cls):
            IPs = []
            for rx in cls.exit_rooms:
                IPs += cls.get_intermediate_providers(rx)

            IPs = list(set(IPs))
            print(f"Rooms directly to exits: {IPs}\n")
            return IPs

        @classmethod
        def get_from_providers(cls, IPs):
            total = 0
            for rx in IPs:
                ask = 0
                for er in cls.exit_rooms:
                    ask += Path[rx][er]
                Rx = DirectProvider(rx, [], ask)
                total += cls.Ask(Rx, ask)
                print(f"Now number of {total} in the exits\n")
            return total

    class DirectProvider(Room):
        def __init__(self, Rx, askers, asked_amount):
            self.name = Rx
            self.DSA = SupplyRecords[Rx]
            self.cur_canGive = self.DSA if self.DSA <= asked_amount else asked_amount
            self.askers = askers
            self.IPs = self.get_IPs() if asked_amount > self.cur_canGive else []
            # It means it has direct supply, take it and update records
            print(f"Room {Rx} has direct supply: {self.DSA}")
            print(f"Room {Rx} currently can give: {self.cur_canGive}")
            if self.DSA > 0:
                SupplyRecords[self.name] -= self.cur_canGive
                print(f"Update the supply records: {SupplyRecords}")

        def get_IPs(self):
            IPs = self.get_intermediate_providers(self.name)
            for asker in self.askers:
                if asker in IPs:
                    IPs.remove(asker)
            return IPs

        def still_need(self, asked):
            stillNeed = asked - self.cur_canGive if (asked - self.cur_canGive) > 0 else 0
            return stillNeed

        def ask_one_in_IPs(self, rx, allow_by_rx, still_need):

            ask_amount = still_need if still_need <= allow_by_rx else allow_by_rx
            print(f"Asking for Room {rx}...")
            askers_from_rx = []
            askers_from_rx += self.askers
            askers_from_rx.append(self.name)
            print(f"Asker chain is now: {askers_from_rx}")
            provider = DirectProvider(rx, askers_from_rx, ask_amount)
            successfully_asked = self.Ask(provider, ask_amount)
            self.cur_canGive += successfully_asked
            # Update quota of  Room x to Room X
            # If ask failed (amount = 0), means it's an invalid provider, block it
            Path[rx][self.name] = 0 if successfully_asked == 0 else Path[rx][self.name] - successfully_asked
            print(f"The quota Room {rx} to Room {self.name} is now: {Path[rx][self.name]}")
            print(f"Room {self.name} totally can give: {self.cur_canGive}\n")
            return self.cur_canGive

    Rooms = len(Path[0])

    IntermediateRooms = list(filter(lambda n: n not in End and n not in Start, range(Rooms)))

    build_supply_records()

    requesters = Requesters()

    return requesters.total


print(solution(entrances, exits, path))

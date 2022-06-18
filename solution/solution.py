from collections import defaultdict
import numpy as np
from Path_5 import entrances, exits, path

SupplyRecords = defaultdict(int)

"""
Model:
    Supplier: entrance rooms, with the amount it can provide to it's immediate rooms
    Direct providers: The rooms that are not the exits, it has non-zero tunnel capacity to it's immediate rooms
    Requester: The exits that ask for maximum amount from their direct providers
    AskChain: The records that keeps tracking chain of askers, in order to prevent loop-asking
    quota: The maximum capacity amount that a provider can give to its asker
"""


def solution(Start, End, Path):

    def build_supply_records(amount_of_rooms):
        """
        Build the dict that track the supply amount to the specific rooms
        (i.e. SR[2] == 15 means the total supply go to Room 2 from entrances is 15 )
        """
        Suppliers = [0 for i in range(amount_of_rooms)]

        # List element addition
        for supplier in Start:
            Suppliers += np.array(Path[supplier])

        # Store the specific amount of supply that can go to which room
        for i in range(amount_of_rooms):
            if Suppliers[i] > 0:
                SupplyRecords[i] = Suppliers[i]

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
        def ask(Rx, asked):
            """
            :param Rx: The Room(provider) to ask
            :param asked: The asked amount
            :return: If the current amount is satisfied, return it; Else it will ask one provider and return the total
            """
            # It means the asked amount == currently can give
            # So no need for asking another DP
            if not Rx.DPs:
                return Rx.cur_canGive
            # Ask one in IPs, and then check if we still need more
            for rx in Rx.DPs:
                still_need = Rx.still_need(asked)
                if still_need == 0:
                    return Rx.cur_canGive
                # Ask the amount that quota allows
                allow_by_rx = Path[rx][Rx.name]
                ask_amount = still_need if still_need <= allow_by_rx else allow_by_rx
                Rx.ask_one_in_DPs(rx, ask_amount)

            return Rx.cur_canGive

    class Requester(Room):
        """
        Attributes:
            DSA: Direct supply amount
            DPs: Direct providers
            total: The total amount it can gather
        """
        exit_rooms = End

        def __init__(self):
            self.DSA = self.get_DSA()
            self.DPs = self.get_DPs()
            self.total = self.get_from_providers(self.DPs) + self.DSA

        @classmethod
        def get_DSA(cls):
            DSA = 0
            for rx in cls.exit_rooms:
                DSA += SupplyRecords[rx]
            return DSA

        @classmethod
        def get_DPs(cls):
            DPs = []
            for rx in cls.exit_rooms:
                DPs += cls.get_intermediate_providers(rx)
            DPs = list(set(DPs))
            return DPs

        @classmethod
        def get_from_providers(cls, DPs):
            total = 0
            # Calculate the quota from one room that connects to every exit room
            #  (i.e. total quota of Room 4(One of the DPs of exits) -> Room 6, Room 7(exits))
            for rx in DPs:
                ask = 0
                for er in cls.exit_rooms:
                    ask += Path[rx][er]
                Rx = DirectProvider(rx, [], ask)
                total += cls.ask(Rx, ask)
            return total

    class DirectProvider(Room):
        """
        Inherited from Room class
        Attributes:
            name: The Room number
            askers: The askers chain(i.e. 5->3->2. -> = ask for)
            cur_canGive: The amount this provider currently can give
            DPs: Direct providers
        """
        def __init__(self, Rx, askers, asked_amount):
            self.name = Rx
            self.askers = askers  # The askers chain
            self.DSA = SupplyRecords[Rx]
            # The amount that currently can give without asking for DPs
            self.cur_canGive = self.DSA if self.DSA <= asked_amount else asked_amount
            # Search for DPs only when currently can give amount is not enough
            self.DPs = self.get_DPs() if asked_amount > self.cur_canGive else []

            # It means it has direct supply, take it and update records
            if self.DSA > 0:
                SupplyRecords[self.name] -= self.cur_canGive

        # Get the valid DPs(the ones that still have quota for me) and filter out the askers(to avoid loop asking)
        def get_DPs(self):
            DPs = self.get_intermediate_providers(self.name)
            for asker in self.askers:
                if asker in DPs:
                    DPs.remove(asker)
            return DPs

        # Calculate for the amount that I still need
        def still_need(self, asked):
            stillNeed = asked - self.cur_canGive if (asked - self.cur_canGive) > 0 else 0
            return stillNeed

        def ask_one_in_DPs(self, rx, ask_amount):
            # Update the askers chain
            askers_from_rx = self.askers
            askers_from_rx.append(self.name)

            # Ask this provider
            provider = DirectProvider(rx, askers_from_rx, ask_amount)
            successfully_asked = self.ask(provider, ask_amount)
            # Update currently can give
            self.cur_canGive += successfully_asked
            # Update quota of  Room x to Room X
            # If ask failed (amount = 0), means it's an invalid provider, block it
            Path[rx][self.name] = 0 if successfully_asked == 0 else Path[rx][self.name] - successfully_asked

    # Get the amount of rooms
    Rooms = len(Path[0])
    # Get the rooms that are not entrances and exits
    IntermediateRooms = list(filter(lambda n: n not in End and n not in Start, range(Rooms)))
    # Build the public supply record(The total amount of bunnies that can go to the immediate rooms)
    build_supply_records(Rooms)
    # Create a Requesters instance
    requesters = Requester()

    return requesters.total


print(solution(entrances, exits, path))

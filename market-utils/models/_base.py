from enum import Enum



class OrderType(Enum):
    BUY = 0
    SELL = 1


# class Order():
#     order_type:OrderType
#     platinum:int
#
#     @property
#     def platinum(self):
#         return self.platinum
#
#     @platinum.setter
#     def platinum(self, value):
#         pass
#
#


#
# class ItemOrder(Order):
#
# class ModOrder(Order):
#     max_rank:bool = False
#
#
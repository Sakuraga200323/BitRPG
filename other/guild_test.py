ITEM = []
pg = Postges(dsn)
client = None
class Cuild:
   global client
   loop = 
   def __init__(self, client):
       client = client
       self.dtd = pg.fetchdict("略")

   def Shop_buy(self, ch, user, item, num):
       if not item in ITEM:
           loop.create_task(ch.send("略"))
           return
       if self.dtd["zaiko"][item] == 0:
           rerturn
       if self.dtd{"zaiko"][item] <= num:
           num = self.dtd{"zaiko"][item]
       item_value = int(100/self.dtd["zaiko"][item]*200)
       if item_value < 100:
           item_value = 100
       else item_value > 400:
           item_value = 400
       p_data = pg.fetchdict("略")[0]
       if p_data["money"] < item_value*num:
           return
       p_data["money"] -= item_value*num
       p_data["item"][item] += num

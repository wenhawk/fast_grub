from escpos.printer import File
from .models import Bill
from datetime import datetime
class Printer():

    @staticmethod
    def printKOT(orders, kid):
        epson = File("/dev/usb/lp0")
        epson.text('\n\n\n\n')
        epson.set(text_type='B',width=2, height=2)
        table = orders[0].table
        epson.text(''+table.name+' KID:'+str(kid)+'\n')
        epson.set(text_type='normal',width=1, height=2)
        for order in orders:
            name = order.item.name
            quantity = order.quantity
            message = str(order.message)
            epson.text(' '+name)
            epson.set(text_type='U',width=1, height=2)
            epson.text(' '+message)
            epson.set(text_type='normal',width=1, height=2)
            epson.text(' x'+str(quantity)+'\n')
        epson.cut()
        epson.close()

    @staticmethod
    def printAJsAddress(epson, bid, table, time):
        epson.set(align='left', text_type='B',width=2, height=2)
        epson.text("     AJ\'s\n")
        epson.set(align='left', text_type='normal',width=1, height=1)
        epson.text("K.K White House, House No.1336\n")
        epson.text(" Don Bosco RD,Murida, Fatorda\n")
        epson.text("        Goa - 403602          \n")
        epson.text("       PH: +91 9923204220     \n")
        timeTable = ''+table+' '+time[0:19]+'\n'
        epson.text(timeTable)
        epson.text('        Bill ID: '+bid+     '\n')

    def printAJsBill(bill, table):
        item_quantitys = bill.getBillSummary()
        bid = str(bill.bid)
        time = str(datetime.now())
        table = table.name.upper()
        total = str(bill.amount)
        epson = File("/dev/usb/lp0")
        Printer.printAJsAddress(bid=bid, table=table, time=time, epson=epson)
        # epson.text('01234567890123456789012345678901\n')
        epson.text('--------------------------------\n')
        epson.set(align='left', text_type='B',width=1, height=1)
        epson.text('Item             Qt  Rate    Amt\n')
        epson.set(align='left', text_type='normal',width=1, height=1)
        epson.text('--------------------------------\n')
        sub_total = 0
        for iq in item_quantitys:
            name = str(iq.get('item').cat)
            cost = str(iq.get('item').cost)
            quantity = str(iq.get('quantity'))
            amount = str(iq.get('quantity') * iq.get('item').cost)
            if len(name) > 16:
                epson.text(txt=name[0:16])
                epson.text(' ')
                Printer.printQuantityCostAndAmount(epson=epson,\
                name=name, cost=cost, quantity=quantity, amount=amount)
                epson.text(txt=name[16:len(name)])
                epson.text(txt='\n')
            else:
                epson.text(txt=name)
                for i in range(16-len(name)):
                    epson.text(' ')
                epson.text(' ')
                Printer.printQuantityCostAndAmount(epson=epson,\
                name=name, cost=cost, quantity=quantity, amount=amount)
        epson.set(align='left', text_type='B',width=1, height=1)
        epson.text('--------------------------------\n')
        epson.text('TOTAL                   Rs '+total+'\n');
        epson.text('\n');
        epson.set(align='left', text_type='normal');
        epson.text('COMPOSITION TAXABLE PERSON\n')
        epson.text('GSTIN: 30AFGPG9096R1ZT\n');
        epson.set(align='left', text_type='B');
        epson.text('       FREE HOME DELIVERY       \n');
        epson.text('\n');
        epson.cut()

    @staticmethod
    def printQuantityCostAndAmount(epson, name, cost, quantity, amount):
        for i in range(2-len(quantity)):
            epson.text(' ')
        epson.text(txt=quantity)
        epson.text('  ')
        for i in range(4-len(cost)):
            epson.text(' ')
        epson.text(txt=cost)
        epson.text('  ')
        for i in range(5-len(amount)):
            epson.text(' ')
        epson.text(txt=amount)
        epson.text(txt='\n')

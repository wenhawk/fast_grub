from . import db
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import relationship
# from sqlalchemy.dialects import mysql


class Item(db.Model):
    __tablename__= 'item'

    iid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.Enum('true', 'false'), nullable=False, default='true')
    cat = db.Column(db.String(100), nullable=False)
    categorys = relationship('ItemCategory', back_populates='item', lazy=True)

    def __repr__(self):
        string = 'Item(iid={}, name={}, cost={}, flag={})'\
        .format(self.iid, self.name, self.cost, self.flag)
        return string

    @staticmethod
    def checkItemExesting(itemName):
        item = Item.query.filter(Item.name.like('%'+itemName+'%')).first()
        return item

    @staticmethod
    def createNewItem(itemName, iid):
        item = Item.query.filter_by(iid=iid).first()
        newItem = Item(cost=item.cost, name=itemName, cat=item.name\
        , flag='false')
        db.session.add(newItem)
        db.session.commit()
        return newItem

class ItemCategory(db.Model):
    __tablename__= 'item_category'

    cid = db.Column(db.Integer, db.ForeignKey('category.cid'), primary_key=True)
    iid = db.Column(db.Integer, db.ForeignKey('item.iid'), primary_key=True)
    item = relationship('Item', back_populates='categorys', lazy=True)
    category = relationship('Category', back_populates='items', lazy=True)

    def __repr__(self):
        string = 'ItemCategory(item={}, category={})'\
        .format(self.item, self.category)
        return string

class Category(db.Model):
    __tablename__= 'category'

    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    items = relationship('ItemCategory', back_populates='category', lazy=True)
    sub_items = relationship('SubItemCategory', back_populates='category', lazy=True)

    def __repr__(self):
        string = 'Category(cid={}, name={})'.format(self.cid, self.name)
        return string

class AjTable(db.Model):
    __tablename__= 'aj_table'

    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    flag = db.Column(db.Enum('true', 'false'), nullable=False, default='true')

    def __repr__(self):
        string = 'AjTable(tid={}, name={}, flag={})'.format(self.tid, self.name, self.flag)
        return string

    def getOrdersNotBilled(self):
        orders = Order.query.filter_by(tid=self.tid,flag='true')\
        .filter(~Order.kid.in_(db.session.query(BillKOT.kid)))\
        .all()
        return orders

    def calculateBillTotal(self):
        orders = self.getOrdersNotBilled()
        total = 0
        for order in orders:
            total = total + order.item.cost * order.quantity
        return total

    def getKots(self):
        orders = Order.query.filter_by(tid=self.tid,flag='true')\
                 .filter(~Order.kid.in_(db.session.query(BillKOT.kid)))\
                 .group_by('kid').all()
        kots = [ order.kot for order in orders ]
        return kots

    def getBillSummary(self):
        orders = self.getOrdersNotBilled()
        item_quantity = Order.getIdenticalItemsFromOrder(orders=orders)
        return item_quantity

    def changeTableStatus(self, flag):
        if flag == 'false':
            self.flag = 'false'
        else:
            self.flag = 'true'
        db.session.commit()

    @staticmethod
    def createTable(form):
        table = AjTable.query\
        .filter(AjTable.name.like('%'+form.name.data+'%'))\
        .first()
        if table:
            table.flag = 'true'
        else:
            table = AjTable(flag='true', name=form.name.data)
            db.session.add(table)
        db.session.commit()

    @staticmethod
    def editTable(tid, form):
        table = AjTable.query.filter_by(tid=tid).first()
        exestingTable = AjTable.query.filter_by(name=form.name.data).first()
        if exestingTable:
            exestingTable.flag = 'true'
        else:
            table.name = form.name.data
        db.session.commit()

class SubItem(db.Model):
    __tablename__= 'sub_item'

    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    flag = db.Column(db.Enum('true', 'false'), nullable=False, default='true')
    categorys = relationship('SubItemCategory', back_populates='sub_item', lazy=True)

    def __repr__(self):
        string = 'SubItem(sid={}, name={}, flag={})'.format(self.sid, self.name, self.flag)
        return string

class Bill(db.Model):
    __tablename__= 'bill'

    bid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=str(datetime.now())[0:19])
    payment_mode = db.Column(db.Enum('cash', 'card', 'credit'), nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    kots = relationship('BillKOT', back_populates='bill', lazy=True)

    def __repr__(self):
        string = 'Bill(bid={}, timestamp={}, payment_mode={}, discount={})'\
        .format(self.bid, self.timestamp, self.payment_mode, self.discount)
        return string

    def __init__(self, payment_mode, discount, *args, **kwargs):
        self.discount = discount
        self.payment_mode = payment_mode
        self.timestamp = str(datetime.now())[0:19]
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getTotalPaymentMode(start_date,end_date,payment_mode):
        cost = db.session.query(func.sum(Bill.amount))\
        .filter(Bill.timestamp.between(start_date,end_date))\
        .filter(Bill.payment_mode == payment_mode)\
        .scalar()
        return cost

    @staticmethod
    def updateWithForm(form):
        bill = Bill.query.filter_by(bid=form.bid.data).first()
        if form.discount.data == None:
            bill.discount = 0
        else:
            bill.discount = form.discount.data
        bill.payment_mode = form.payment_mode.data
        bill.amount = bill.caclulateBillAmount()
        db.session.commit()
        return bill


    @staticmethod
    def getTotalCost(start_date,end_date):
        cost = db.session.query(func.sum(Bill.amount))\
        .filter(Bill.timestamp.between(start_date,end_date))\
        .filter(Bill.payment_mode != 'credit')\
        .scalar()
        return cost

    def getKots(self):
        bill_kots = self.kots
        kots = [ bill_kot.kot for bill_kot in bill_kots ]
        return kots

    def getOrders(self):
        orders = db.session.query(Order)\
        .filter(Order.kid == BillKOT.kid)\
        .filter(BillKOT.bid == self.bid)\
        .filter(Order.flag == 'true')\
        .all()
        return orders

    def getBillSummary(self):
        orders = self.getOrders()
        item_quantity = Order.getIdenticalCategoryFromOrder(orders=orders)
        return item_quantity

    def getTable(self):
        table = db.session.query(AjTable)\
        .filter(Order.kid == BillKOT.kid)\
        .filter(BillKOT.bid == self.bid)\
        .filter(Order.tid == AjTable.tid)\
        .group_by('orders.tid').first()
        return table

    def caclulateBillAmount(self):
        orders = self.getOrders()
        cost = 0
        for order in orders:
            cost += order.item.cost * order.quantity
        return int(cost-(cost*(self.discount)/100))

    def caclulateBillAmountWithDisount(self):
        orders = self.getOrders()
        cost = 0
        for order in orders:
            cost += order.item.cost * order.quantity
        return int(cost)

class KOT(db.Model):
    __tablename__= 'kot'

    kid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=str(datetime.now())[0:19])
    flag = db.Column(db.Enum('true', 'false'), nullable=False, default='true')
    orders = relationship('Order', back_populates='kot', lazy=True)
    bill = relationship('BillKOT', back_populates='kot', lazy=True)

    def __init__(self, *args, **kwargs,):
        self.flag = 'true'
        self.timestamp = str(datetime.now())[0:19]
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        string = 'KOT(kid={}, timestamp={}, flag={})'\
        .format(self.kid, self.timestamp, self.flag)
        return string

    def getOrders(self):
        orders = Order.query.filter_by(kid=self.kid,flag='true').all()
        return orders

    def getTable(self):
        order = Order.query.filter_by(kid=self.kid).group_by('tid').first()
        if order:
            return order.table
        else:
            return None

class BillKOT(db.Model):
    __tablename__= 'bill_kot'

    bid = db.Column(db.Integer, db.ForeignKey('bill.bid'), primary_key=True)
    kid = db.Column(db.Integer, db.ForeignKey('kot.kid'), primary_key=True)
    flag = db.Column(db.Enum('true','false'), nullable=False, default='true')
    bill = relationship('Bill', back_populates='kots', lazy=True)
    kot = relationship('KOT', back_populates='bill', lazy=True)

    def __repr__(self):
        string = 'BillKOT(bill={}, kot={})'\
        .format(self.bill, self.kot)
        return string

    def __init__(self, kid, bid, *args, **kwargs,):
        self.kid = kid
        self.bid = bid
        self.flag = 'true'
        db.session.add(self)
        db.session.commit()

class Order(db.Model):
    __tablename__= 'orders'

    kid = db.Column(db.Integer, db.ForeignKey('kot.kid'), primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('aj_table.tid'), primary_key=True)
    iid = db.Column(db.Integer, db.ForeignKey('item.iid'), primary_key=True)
    rank = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    flag = db.Column(db.Enum('true','false'), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    table = relationship('AjTable', lazy=True)
    item = relationship('Item', lazy=True)
    kot = relationship('KOT', back_populates='orders', lazy=True)

    @staticmethod
    def getOrdersByDate(start_date,end_date,sortBy):
        orders = db.session.query(Order)\
        .filter(Order.kid == KOT.kid)\
        .filter(KOT.timestamp >= start_date)\
        .filter(KOT.timestamp <= end_date)\
        .filter(Order.flag == 'true')\
        .all()
        if sortBy == 'item':
            item_quantity = Order.getIdenticalItemsFromOrder(orders=orders)
        else:
            item_quantity = Order.getIdenticalCategoryFromOrder(orders=orders)
        return item_quantity

    @staticmethod
    def getTotalCost(item_quantity):
        totalCost = 0
        for iq in item_quantity:
            totalCost = totalCost + (iq.get('quantity') * iq.get('item').cost)
        return totalCost

    @staticmethod
    def saveOrders(kot,kot_form,tid):
        for i,iid in enumerate(kot_form.iid.data):
            item = Item.checkItemExesting(itemName = kot_form.item_name[i].data)
            if item:
                order = Order(kid=kot.kid, tid=tid, iid=item.iid,\
                quantity=kot_form.quantity[i].data,flag='true',message=kot_form.message[i].data,\
                status=0, rank=kot_form.rank[i].data)
            else:
                newItem = Item.createNewItem(itemName=kot_form.item_name[i].data\
                ,iid=iid)
                order = Order(kid=kot.kid, tid=tid, iid=newItem.iid,\
                quantity=kot_form.quantity[i].data,flag='true',message=kot_form.message[i].data,\
                status=0, rank=kot_form.rank[i].data)
            db.session.add(order)
        db.session.commit()

    @staticmethod
    def getIdenticalItemsFromOrder(orders):
        item_quantity = []
        for order in orders:
            for iq in item_quantity:
                if iq.get('item') == order.item :
                    iq['quantity'] = iq.get('quantity') + order.quantity
                    break
            else:
                item_quantity.append({'quantity':order.quantity, 'item':order.item})
        return item_quantity

    @staticmethod
    def getIdenticalCategoryFromOrder(orders):
        item_quantity = []
        for order in orders:
            for iq in item_quantity:
                if iq.get('item').cat == order.item.cat :
                    iq['quantity'] = iq.get('quantity') + order.quantity
                    break
            else:
                item_quantity.append({'quantity':order.quantity, 'item':order.item})
        return item_quantity

    @staticmethod
    def getOrdersServed():
        orders = Order.query.filter_by(flag='true',status=1)\
                 .filter(~Order.kid.in_(db.session.query(BillKOT.kid))).all()
        return orders

    @staticmethod
    def getOrdersNotServed():
        orders = Order.query.filter_by(flag='true',status=0)\
                 .filter(~Order.kid.in_(db.session.query(BillKOT.kid))).all()
        return orders

    @staticmethod
    def editOrders(form):
        for i,iid in enumerate(form.iid.data):
            order = Order.query.filter_by(iid=iid, kid=form.kid[i].data,\
                                          rank=form.rank[i].data).first()
            order.message = form.message[i].data
            order.quantity = form.quantity[i].data
            order.flag = form.flag[i].data
            db.session.commit()

    def changeOrderStatus(self, status):
        if status == '1':
            self.status = 1
        else:
            self.status = 0
        db.session.commit()


    def __repr__(self):
        string = 'Order(kot={}, item={}, table={}, quantity={}, flag={}, message={})'\
        .format(self.kot, self.item, self.table, self.quantity, self.flag, self.message)
        return string


class SubItemCategory(db.Model):
    __tablename__= 'sub_item_category'

    cid = db.Column(db.Integer, db.ForeignKey('category.cid'), primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('sub_item.sid'), primary_key=True)
    sub_item = relationship('SubItem', back_populates='categorys', lazy=True)
    category = relationship('Category', back_populates='sub_items', lazy=True)

    def __repr__(self):
        string = 'SubItemCategory(sub_item={}, category={})'\
        .format(self.sub_item, self.category)
        return string

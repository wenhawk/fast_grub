from . import app
from flask import render_template, url_for, redirect, request, jsonify
from .models import Item, KOT, Order, AjTable, Bill, BillKOT, SubItem\
                    ,Category ,ItemCategory, SubItemCategory
from .forms import ItemForm, KOTForm, OrderForm\
, OrderStatusForm, BillForm, TableForm, ReportForm , SearchForm, IdSearchForm, TableCreateForm
from .printer import Printer
from . import db
from datetime import datetime
from sqlalchemy.sql.expression import desc


@app.route('/')
def home():
    form = TableForm()
    aj_tables = AjTable.query.filter_by(flag='true').all()
    return render_template('home.html',aj_tables=aj_tables, form=form)

################
#### Report ####
################

@app.route('/report/view' ,methods=['GET','POST'])
def report():
    form = ReportForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        sortBy = form.sortBy.data
        item_quantity = Order.getOrdersByDate(start_date=\
                                start_date, end_date=end_date, sortBy=sortBy)
        cost = Bill.getTotalCost(start_date=start_date\
                                    ,end_date=end_date)
        cash = Bill.getTotalPaymentMode(start_date=start_date\
                                    ,end_date=end_date,payment_mode='cash')
        card = Bill.getTotalPaymentMode(start_date=start_date\
                                    ,end_date=end_date,payment_mode='card')
        return render_template('view_reports.html'\
                    , item_quantity=item_quantity\
                    , cost=cost,card=card,cash=cash, sortBy=sortBy)
    return render_template('report.html', form=form)

###############
#### TABLE ####
###############

@app.route('/table/trash<int:page>' ,methods=['GET','POST'])
def trash(page):
    form = TableForm()
    tableSearch = SearchForm()
    if not tableSearch.name.data:
        tableSearch.name.data=""
    paginate = aj_tables = AjTable.query\
        .filter(AjTable.name.like('%'+tableSearch.name.data+'%'))\
        .paginate(page,15,False)
    aj_tables = paginate.items
    return render_template('trash.html', aj_tables=aj_tables, form=form\
                           ,paginate=paginate)

@app.route('/table/edit_table_status' ,methods=['GET','POST'])
def edit_table_status():
    form = TableForm()
    if form.validate_on_submit():
        aj_table = AjTable.query.filter_by(tid=form.tid[0].data).first()
        aj_table.changeTableStatus(flag=form.flag[0].data)
    return redirect(url_for('home'))

#############
#### KOT ####
#############

@app.route('/kot/view<int:tid>', methods=['GET','POST'])
def view_kots(tid):
    aj_table = AjTable.query.filter_by(tid=tid).first()
    kots = aj_table.getKots()
    if kots:
        return render_template('view_kots.html', kots=kots, table=aj_table)
    return redirect(url_for('home'))

@app.route('/kot/print<int:kid>', methods=['GET','POST'])
def print_kot(kid):
    form = KOTForm()
    kot = KOT.query.filter_by(kid=kid).first()
    orders = kot.orders
    if request.method == 'POST':
        try:
            Printer.printKOT(orders=orders, kid=kid)
        except FileNotFoundError:
            print("----------->PRINTER NOT CONNECTED<--------")
        return redirect(url_for('home'))
    return render_template('print_kot.html', orders=orders, form=form)

@app.route('/kots/edit<int:tid>', methods=['GET','POST'])
def edit_kots(tid):
    aj_table = AjTable.query.filter_by(tid=tid).first()
    form = OrderForm()
    orders = aj_table.getOrdersNotBilled()
    if form.validate_on_submit():
        Order.editOrders(form)
        if form.printFlag.data == 'yes':
            try:
                Printer.printKOT(orders=orders,kid=kid)
            except FileNotFoundError:
                print("----------->PRINTER NOT CONNECTED<--------")
                return redirect(url_for('home'))
        return redirect(url_for('home'))
    return render_template('edit_kot.html',orders=orders, form=form, title='kots',tid=tid)

@app.route('/kot/edit<int:kid>', methods=['GET','POST'])
def edit_kot(kid):
    form = OrderForm()
    kot = KOT.query.filter_by(kid=kid).first()
    orders = kot.getOrders()
    if orders:
        if form.validate_on_submit():
            Order.editOrders(form)
            bill = db.session.query(Bill).filter(BillKOT.kid == kid)\
                             .filter(Bill.bid == BillKOT.bid).first()
            bill_kot = BillKOT.query.filter_by(kid=kid).count()
            if bill_kot > 0:
                bill.amount = bill.caclulateBillAmount()
                db.session.commit()
            if form.printFlag.data == 'yes':
                try:
                    Printer.printKOT(orders=orders,kid=kid)
                except FileNotFoundError:
                    print("----------->PRINTER NOT CONNECTED<--------")
            return redirect(url_for('home'))
        return render_template('edit_kot.html',orders=orders, form=form, title='kot',kid=kid)
    return redirect(url_for('admin_view_kots',page=1))

@app.route('/kot/generate<int:tid>', methods=['GET','POST'])
def generate_kot(tid):
    form = KOTForm()
    if form.validate_on_submit():
        if len(form.iid.data) > 0:
            kot = KOT(flag='true')
            Order.saveOrders(kot=kot,kot_form=form,tid=tid)
            return redirect(url_for('print_kot',kid=kot.kid))
        else:
            return redirect(url_for('home'))
    aj_table = AjTable.query.filter_by(tid=tid).first()
    items = Item.query.filter_by(flag='true').all()
    return render_template('generate_kot.html',form=form,items=items,aj_table=aj_table)


## API to get all Items: Categorys and SubItems
@app.route('/item/jason/<int:iid>', methods=['GET'])
def item_jason(iid):
    sub = {}
    item = Item.query.filter_by(iid=iid).first()
    categorys = [ item_category.category for item_category in item.categorys ]
    if len(categorys) != 0:
        sub_item_categorys = [ category.sub_items for category in categorys ]
        sub = [ {'name':sub_item_category[0].category.name, 'iid':sub_item_category[0].category.cid,'values':[ {'name':sub_item_cat.sub_item.name, 'sid':sub_item_cat.sub_item.sid} for sub_item_cat in sub_item_category ]} for sub_item_category in sub_item_categorys ]
    sub = jsonify(item=sub)
    return sub

##################
#### ADMIN   ####
##################

@app.route('/admin/view_kots<int:page>', methods=['GET', 'POST'])
def admin_view_kots(page):
    form = IdSearchForm()
    if form.validate_on_submit():
        paginate = KOT.query.filter_by(kid=form.id.data)\
        .paginate(page,9,False)
    else:
        paginate = KOT.query.order_by(desc('kid')).paginate(page,8,False)
    kots = paginate.items
    tables = [ kot.getTable() for kot in kots ]
    return render_template('admin/view_kots.html', kots=kots, tables=tables, \
                            paginate=paginate, form=form)


@app.route('/admin/view_bills<int:page>', methods=['GET', 'POST'])
def view_bills(page):
    form = IdSearchForm()
    if form.validate_on_submit():
        paginate = Bill.query.filter_by(bid=form.id.data)\
        .paginate(page, 9, False)
    else:
        paginate = Bill.query.order_by(desc('bid')).paginate(page, 8, False)
    bills = paginate.items
    table_cost = [ (bill.amount,bill.getTable()) for bill in bills ]
    return render_template('admin/view_bills.html', bills=bills, table_cost=table_cost,\
                            paginate=paginate, form=form)

@app.route('/admin/view_table<int:page>' ,methods=['GET','POST'])
def view_table(page):
    form = TableCreateForm()
    if form.validate_on_submit():
        paginate = AjTable.query\
        .filter(AjTable.name.like('%'+form.name.data+'%'))\
        .paginate(page, 8, False)
    else:
        paginate = AjTable.query.paginate(page, 8, False)
    tables = paginate.items
    return render_template('admin/view_table.html', form=form\
    , paginate=paginate, tables=tables)


@app.route('/admin/edit_table<int:tid>' ,methods=['GET','POST'])
def edit_table(tid):
    title = 'EDIT'
    form = TableCreateForm()
    if form.validate_on_submit():
        AjTable.editTable(tid=tid, form=form)
        return redirect(url_for('home'))
    table = AjTable.query.filter_by(tid=tid).first()
    form.name.data = table.name
    return render_template('admin/create_table.html', form=form, title=title, table=table)

@app.route('/admin/create_table' ,methods=['GET','POST'])
def create_table():
    title = 'CREATE'
    form = TableCreateForm()
    if form.validate_on_submit():
        AjTable.createTable(form)
        return redirect(url_for('home'))
    return render_template('admin/create_table.html', form=form, title=title)

@app.route('/admin/create_item' ,methods=['GET','POST'])
def create_item():
    title = 'CREATE'
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, cost=form.cost.data)
        db.session.add(item)
        try:
            db.session.commit()
        except:
            print("----------->Item already present ",item.name,'<---------')
        return redirect(url_for('view_items',page=1))
    return render_template('admin/create_item.html', form=form, title=title)

@app.route('/admin/edit_item<int:iid>' ,methods=['GET','POST'])
def edit_item(iid):
    title = 'EDIT'
    item = Item.query.filter_by(iid=iid).first()
    form = ItemForm()
    if form.validate_on_submit():
        item.name = form.name.data
        item.cost = form.cost.data
        db.session.add(item)
        try:
            db.session.commit()
        except:
            print("----------->Item already present ",item.name,'<---------')
        return redirect(url_for('view_items',page=1))
    else:
        form.name.data = item.name
        form.cost.data = item.cost
    return render_template('admin/create_item.html', form=form, title=title, iid=iid)

@app.route('/admin/view_items<int:page>', methods=['GET','POST'])
def view_items(page):
    form = SearchForm()
    if form.validate_on_submit():
        paginate = Item.query.filter(Item.name.like('%'+form.name.data+'%'))\
                   .filter_by(flag='true')\
                   .paginate(page, 8, False)
    else:
        paginate = Item.query.filter_by(flag='true').paginate(page, 8, False)
    items = paginate.items
    return render_template('admin/view_items.html', form=form\
                           ,items=items,paginate=paginate)

@app.route('/admin/view_sub_items<int:page>', methods=['GET','POST'])
def view_sub_items(page):
    form = SearchForm()
    if form.validate_on_submit():
        paginate = SubItem.query.filter(SubItem.name.like('%'+form.name.data+'%'))\
                   .filter_by(flag='true')\
                   .paginate(page, 8, False)
    else:
        paginate = SubItem.query.filter_by(flag='true').paginate(page, 8, False)
    items = paginate.items
    return render_template('admin/view_sub_items.html', form=form\
                           ,items=items,paginate=paginate)

@app.route('/admin/view_categories<int:page>', methods=['GET','POST'])
def view_categories(page):
    form = SearchForm()
    if form.validate_on_submit():
        paginate = Category.query.filter(Category.name.like('%'+form.name.data+'%'))\
                   .paginate(page, 8, False)
    else:
        paginate = Category.query.paginate(page, 8, False)
    categories = paginate.items
    return render_template('admin/view_categories.html', form=form\
                           ,categories=categories,paginate=paginate)

@app.route('/admin/view_item_category<int:page>', methods=['GET','POST'])
def view_item_category(page):
    form = SearchForm()
    paginate = ItemCategory.query.paginate(page, 8, False)
    item_categories = paginate.items
    return render_template('admin/view_item_category.html', form=form\
                           ,item_categories=item_categories,paginate=paginate)

@app.route('/admin/view_sub_item_category<int:page>', methods=['GET','POST'])
def view_sub_item_category(page):
    form = SearchForm()
    paginate = SubItemCategory.query.paginate(page, 8, False)
    sub_item_categories = paginate.items
    return render_template('admin/view_sub_item_category.html', form=form\
                           ,sub_item_categories=sub_item_categories,paginate=paginate)


##################
#### BILL ####
##################
@app.route('/bill/generate<int:tid>', methods=['GET','POST'])
def generate_bill(tid):
    aj_table = AjTable.query.filter_by(tid=tid).first()
    quantity_items = aj_table.getBillSummary()
    if quantity_items:
        form = BillForm()
        bill_total = aj_table.calculateBillTotal()
        return render_template('print_bill.html', \
        quantity_items=quantity_items, total=bill_total, aj_table=aj_table, form=form)
    return redirect(url_for('home'))

@app.route('/bill/print', methods=['GET', 'POST'])
def print_bill():
    form = BillForm()
    if form.validate_on_submit:
        aj_table = AjTable.query.filter_by(tid=form.tid.data).first()
        kots = aj_table.getKots()
        if kots:
            bill = Bill(payment_mode=form.payment_mode.data, discount=form.discount.data)
            for kot in kots:
                BillKOT(kid=kot.kid, bid=bill.bid)
            bill.amount = bill.caclulateBillAmount()
            db.session.commit()
            if form.printFlag.data == 'yes':
                try:
                    Printer.printAJsBill(bill=bill, table=aj_table)
                except FileNotFoundError:
                    print("----------->PRINTER NOT CONNECTED<--------")
                    return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/bill/update_and_print_bill', methods=['GET', 'POST'])
def update_and_print_bill():
    form = BillForm()
    if form.validate_on_submit:
        bill = Bill.updateWithForm(form=form)
        if form.printFlag.data == 'yes':
            try:
                Printer.printAJsBill(bill=bill, table=bill.getTable())
            except FileNotFoundError:
                print("----------->PRINTER NOT CONNECTED<--------")
                return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/bill/update<int:bid>', methods=['GET','POST'])
def edit_bill(bid):
    form = BillForm()
    bill = Bill.query.filter_by(bid=bid).first()
    table = bill.getTable()
    quantity_items = bill.getBillSummary()
    if quantity_items:
        bill = bill
        return render_template('edit_bill.html',quantity_items=quantity_items\
        , aj_table=table, form=form, bill=bill)
    return redirect(url_for('home'))

##################
#### Orders ####
##################

@app.route('/orders/edit_order_status', methods=['GET','POST'])
def edit_order_status():
    form = OrderStatusForm()
    s_orders = Order.getOrdersServed()
    ns_orders = Order.getOrdersNotServed()
    if form.validate_on_submit():
        order = Order.query.filter_by(iid=form.iid[0].data, tid=form.tid[0].data,\
                                rank=form.rank[0].data, kid=form.kid[0].data).first()
        order.changeOrderStatus(status=form.status[0].data)
        return redirect(url_for('edit_order_status'))
    return render_template('edit_order_status.html',s_orders=s_orders, \
                            ns_orders=ns_orders, form=form)

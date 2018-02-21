from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FieldList, DateField
from wtforms.validators import DataRequired, optional, NumberRange
from wtforms.widgets import HiddenInput

class ItemForm(FlaskForm):
    name = StringField('ITEM NAME', validators=[DataRequired()])
    cost = IntegerField('COST', validators=[DataRequired()])

class TableForm(FlaskForm):
    tid = FieldList(IntegerField('tid', validators=[DataRequired()]))
    flag = FieldList(SelectField('flag', choices=[('true','Active'),('false','Delete')]))

class SearchForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])

class IdSearchForm(FlaskForm):
        id = IntegerField('ID', validators=[DataRequired()])

class KOTForm(FlaskForm):
    iid = FieldList(IntegerField('ITEM ID', validators=[DataRequired()]))
    quantity = FieldList(IntegerField('QUANTITY', validators=[DataRequired()]))
    message = FieldList(StringField('MESSAGE'))
    rank = FieldList(IntegerField('RANK', validators=[DataRequired()]))
    item_name = FieldList(StringField('Item Name', validators=[DataRequired()]))


class OrderForm(FlaskForm):
    flag = FieldList(SelectField('Order Status', choices=[('true','Active'),('false','Delete')]))
    quantity = FieldList(IntegerField('QUANTITY', validators=[DataRequired()]))
    message = FieldList(StringField('MESSAGE'))
    rank = FieldList(IntegerField('RANK', validators=[DataRequired()]))
    tid = FieldList(IntegerField('Tid'))
    iid = FieldList(IntegerField('ITEM ID', validators=[DataRequired()]))
    kid = FieldList(IntegerField('Kot ID',validators=[DataRequired()]))
    printFlag = SelectField('PRINT', choices=[('yes','YES'),('no','NO')], validators=[DataRequired()])

class OrderStatusForm(FlaskForm):
    status = FieldList(SelectField('Served or not', choices=[('0','Not Served'),('1','Served')]))
    rank = FieldList(IntegerField('RANK', validators=[DataRequired()]))
    tid = FieldList(IntegerField('Tid'),  validators=[DataRequired()])
    iid = FieldList(IntegerField('ITEM ID', validators=[DataRequired()]))
    kid = FieldList(IntegerField('Kot ID List', validators=[DataRequired()]))

class BillForm(FlaskForm):
    payment_mode = SelectField('Payment Mode', choices=[('card','Card'),('cash','Cash')])
    discount = IntegerField('Discount', validators=[NumberRange(min=0, max=100)])
    bid = IntegerField('BIll ID')
    tid = IntegerField('tid', validators=[DataRequired()])
    printFlag = SelectField('PRINT', choices=[('yes','YES'),('no','NO')], validators=[DataRequired()])

class ReportForm(FlaskForm):
    start_date = DateField('Start Date',  format='%Y-%m-%d' ,validators=[DataRequired()])
    end_date = DateField('Start Date',  format='%Y-%m-%d')
    sortBy = SelectField('Select Field', choices=[('item','Item')\
                        ,('category','Category')], validators=[DataRequired()])

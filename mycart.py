import random
import pandas as pd
from pandas import DataFrame
import click
from sqllite import *
import uuid
import datetime
from  pyfiglet import Figlet


@click.group(chain=True)
def cli():
    f=Figlet(font='slant')
    print(f.renderText('M y c a r t'))
    pass

@cli.command()
@click.password_option('-username',required=True,confirmation_prompt=False,hide_input=False)
@click.password_option('-password',required=True,confirmation_prompt=True,hide_input=True)
def set_admin(username,password):
    """Admin registration"""
    conn = create_db()
    conn.execute("INSERT INTO ADMIN VALUES(?,?)",(username,password))
    conn.commit()
    click.echo('admin added successfully')

@cli.command()
def register():
    """User registration"""
    user_name = click.prompt('Please enter a username', type=str)
    password= click.prompt('Please enter a password', type=str,hide_input=True)
    conn=create_db()
    id=random.randint(1,100000)
    conn.execute("INSERT INTO USERS VALUES (?,?)",(user_name,password))
    conn.commit()




@cli.command()
@click.password_option('--adminpassword',confirmation_prompt=False,required=True)
def add_categories(adminpassword):
    """Add Categories"""
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT password from ADMIN")
    password = cur.fetchone()
    if password  and adminpassword == password[0]:
        name = click.prompt('Please enter type of categories you want', type=str)
        name=name.lower()
        id = random.randint(1, 100000)
        conn.execute("INSERT INTO CATEGORIES VALUES (?,?)", (id,name))
        conn.commit()
        flag = click.prompt('do you want to continue', type=str )
        if flag == 'yes':
            cli()
        else:
            click.echo('Categories added successfully')
            print('\n')
            print(pd.read_sql_query("SELECT * FROM  CATEGORIES",conn))
    else:
        click.echo('Incorrect Password')


@cli.command()
@click.password_option('--adminpassword',confirmation_prompt=False,required=True)
def add_products(adminpassword):
    """Add Products to the categories"""
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT password from ADMIN")
    password = cur.fetchone()
    if password and adminpassword == password[0]:
        name = click.prompt('Please enter product name', type=str)
        description=click.prompt('Please enter product description',type=str)
        amount = click.prompt('Please enter product amount', type=int)
        product_category=click.prompt('Please enter product category name',type=str)
        cur=conn.cursor()
        cur.execute("SELECT category_id FROM CATEGORIES WHERE name=:name",{'name':str(product_category)})
        category_id=cur.fetchone()
        if category_id:
            category_id = category_id[0]
            id = random.randint(1, 100000)
            conn.execute("INSERT INTO PRODUCTS VALUES (?,?,?,?,?)", (id,name,description,amount,int(category_id)))
            conn.commit()
            flag = click.prompt('do you want to continue yes/no', type=str)
            if flag.lower() == 'yes':
                cli()
            else:
                click.echo('Categories added successfully')
                print('\n')
                print(pd.read_sql_query("SELECT product_name,description,amount from PRODUCTS",conn))
        else:

            click.echo('Please enter correct category')
    else:
        click.echo('Incorrect password')

@cli.command()
def view_categories():
    """View list of all categories of products"""
    conn = create_db()
    print(pd.read_sql_query("SELECT name FROM CATEGORIES", conn))


@cli.command()
def view_all_products():
    """View all available product details"""
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT product_name FROM PRODUCTS")
    products = cur.fetchone()
    if products:
        print(pd.read_sql_query("SELECT product_name,description,amount FROM PRODUCTS", conn))
    else:
        click.echo('No products currently,Please Visit Again in sometime')



@cli.command()
def view_product():
    """View specific product details"""
    conn = create_db()
    cur=conn.cursor()
    cur.execute("SELECT product_name FROM PRODUCTS")
    product=cur.fetchone()
    if product:
        product_name = click.prompt('enter the product name to view details', type=str)
        print('\n')
        print(pd.read_sql_query("SELECT product_name,description,amount FROM PRODUCTS WHERE product_name=:product_name",conn,params={'product_name':product_name}))
    else:
        click.echo('No products currently,Please Visit Again in sometime')


@cli.command()
@click.password_option('--adminpassword',confirmation_prompt=False,required=True)
def view_user_cart(adminpassword):
    """View carts items and generated bills of every user"""
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT password from ADMIN")
    password = cur.fetchone()
    if password and adminpassword == password[0]:    
        conn = create_db()
        cur=conn.cursor()
        cur.execute("SELECT * FROM USERCART")
        usercart=cur.fetchone()
        if usercart:
            print(pd.read_sql_query("SELECT * FROM USERCART", conn))
        else:
            click.echo('Its Empty')
    else: 
        click.echo("Incorrect Password!!")       

@cli.command()
@click.option('--username', prompt=True,required=True,
                      hide_input=False)
@click.option('--password', prompt=True,required=True,
                      hide_input=True)
def add_my_cart(username,password):
    """
    Add products to your cart
    """
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT username,password FROM USERS WHERE username=:username AND password=:password",
                           {"username": username, 'password': password})
    user_name = cur.fetchone()
    if user_name is not None and username==user_name[0] and password == user_name[1]:
        user_name = user_name[0]
        product_name = click.prompt('enter product name to add', type=str)
        #product_name=product_name.lower()
        cur.execute("SELECT amount FROM PRODUCTS WHERE product_name=:product_name",{'product_name':product_name})
        amount=cur.fetchone()
        if amount is not None:
            amount=amount[0]
            id = random.randint(1, 10000000)
            conn.execute("INSERT INTO MYCART VALUES(?,?,?,?)", (id,str(product_name),int(amount),str(user_name)))
            conn.execute("INSERT INTO USERCART VALUES(?,?,?,?)", (id,str(product_name),int(amount),str(user_name)))
            conn.commit()
            click.echo('Your cart:')
            print('\n')
            print(pd.read_sql_query(
                "SELECT product_name,amount FROM MYCART WHERE username=:username", conn,
                params={'username': str(user_name)}))

        else:
            click.echo('Product with this name not, Please enter valid product name')
    else:
        click.echo('Incorrect Username Or Password')

@cli.command()
@click.option('--username', prompt=True,required=True,
                      hide_input=False)
@click.option('--password', prompt=True,required=True,
                      hide_input=True)
def remove_from_cart(username,password):
    """Remove products from cart"""
    conn=create_db()
    cur = conn.cursor()
    cur.execute("SELECT username,password FROM USERS WHERE username=:username AND password=:password",
                {"username": username, 'password': password})
    user_name = cur.fetchone()
    if user_name is not None and username == user_name[0] and password == user_name[1]:
        user_name = user_name[0]


        click.echo('Your cart:')
        print('\n')
        print(pd.read_sql_query(
            "SELECT product_name,amount FROM MYCART WHERE username=:username", conn,
            params={'username': str(user_name)}))
        product_name = click.prompt('enter product name to remove', type=str)
        conn.execute("DELETE FROM MYCART WHERE product_name=:product_name COLLATE NOCASE",
                                    {'product_name': product_name})
        conn.execute("DELETE FROM USERCART WHERE product_name=:product_name COLLATE NOCASE",
                                    {'product_name': product_name})
        conn.commit()
        click.echo('Product removed from your cart')
    else:
        click.echo('Incorrect Username or password')



@cli.command()
@click.option('--username', prompt=True,required=True,
                      hide_input=False)
@click.option('--password', prompt=True,required=True,
                      hide_input=True)
def checkout(username,password):
    """Checkout with all the products in your cart"""
    current_date=datetime.datetime.now()
    date=current_date.date()
    conn = create_db()
    cur = conn.cursor()
    cur.execute("SELECT username,password FROM USERS WHERE username=:username AND password=:password",
                {"username": username, 'password': password})
    user_name = cur.fetchone()
    if user_name is not None and username == user_name[0] and password == user_name[1]:
        user_name = user_name[0]
        cur.execute("SELECT username FROM MYCART WHERE username=:username", {'username': str(user_name)})
        check_cart=cur.fetchone()

        if check_cart:
                user_cart=conn.execute("SELECT SUM(amount) FROM MYCART WHERE username=:username",{'username':user_name})
                amount=user_cart.fetchone()[0]
                print(pd.read_sql_query(
                    "SELECT product_name,amount FROM MYCART WHERE username=:username", conn,
                      params={'username': str(user_name)}))
                print('')
                print('\n')

                user_cart = conn.execute("SELECT SUM(amount) FROM MYCART WHERE username=:username", {'username': user_name})
                amount = user_cart.fetchone()[0]
                print(pd.read_sql_query(
                    "SELECT product_name,amount FROM MYCART WHERE username=:username", conn,
                    params={'username': str(user_name)}))
                conn.execute("DELETE  FROM MYCART WHERE username=:username", {'username': user_name})
                conn.commit()

                if amount >10000:
                    final_bill=amount-500

                    print('\n')
                    print('Total Bill Amount =', amount)
                    print('Discounted Amount = 500')
                    print('Amount to be paid =', final_bill)
                else:
                    print('Amount to be paid =', amount)

        else:
            click.echo('Cart is Empty, Please Add some products in cart first')
    else:
        click.echo('Incorrect Username or password')

@click.group()
def main():
    pass

if __name__ == '__main__':
    cli()



#--------------------------------------------------------------------------------------------------------------------------


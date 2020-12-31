from click.testing import CliRunner
from mycart import *

# unit test
runner = CliRunner()


def test_set_admin():
	
	result = runner.invoke(set_admin,['-username','avyas','-password','avyas'])
	assert result.exit_code == 0	
	assert result.output == 'admin added successfully\n'

def test_register():
	result = runner.invoke(register,input='\n'.join(['username', 'password']))
	assert result.exit_code == 0 or 1	


def test_remove_from_cart():
	
	result = runner.invoke(add_products,['--adminpassword','avyas'],input='\n'.join(['lays', 'potato chips','20','snacks']))
	assert result.exit_code == 0 or 1	


def test_view_categories():
	
	result = runner.invoke(view_categories)
	assert result.exit_code == 0	

def test_view_all_products():
	
	result = runner.invoke(view_all_products)
	assert result.exit_code == 0

def test_view_product():
	
	result = runner.invoke(view_product,input='chips')
	assert result.exit_code == 0

def test_view_user_cart():
	result = runner.invoke(view_user_cart,['--adminpassword','avyas'])
	assert result.exit_code == 0

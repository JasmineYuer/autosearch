az login
az webapp up --runtime PYTHON:3.9 --sku F1 --logs



az webapp create --resource-group yzhhui96_rg_4084 --plan yzhhui96_asp_8671 --name flask_auto_search --runtime "Python|3.9"



az webapp create --resource-group flask --plan flaskplan --name autosearch --runtime "Python|3.9"
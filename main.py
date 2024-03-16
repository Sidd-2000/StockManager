from functools import wraps
from flask import Flask, redirect, render_template, request, send_file, session, url_for
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_keysiddharth210835mulund.ac.in'

def authenticate(username, password):
    # Example authentication logic - replace this with your actual authentication logic
    return username == 'ganesh@2020' and password == 'P@ssword'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def hello_world():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if authenticate(username, password):
            session['logged_in'] = True
            return redirect(url_for('adminpanel'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/adminpanel')
@login_required
def adminpanel():
    return render_template('adminpanel.html')

@app.route('/purchase',methods=['GET','POST'])
@login_required
def purchase():
    df = pd.read_excel('purchase.xlsx')
    medicine_names = df['medname'].unique().tolist()
    df = pd.read_excel('purchase.xlsx')
    if request.method == 'POST':
        medicine_list = []
        medicin_name = request.form.get('medname')
        Pdate = request.form.get('Pdate')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        expiry = request.form.get('expiry')
        medicine_list.append({
            'medname': medicin_name,
            'Pdate': Pdate,
            'quantity': quantity,
            'price': price,
            'expiry': expiry
        })
        try:
            df = pd.read_excel('purchase.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame()
        df = df._append(medicine_list, ignore_index=True)
        df.to_excel('purchase.xlsx', index=False)
        all_data = df.to_dict(orient='records')
        return redirect(url_for('purchase',all_data=all_data,medname=medicine_names))
    else:
        df = pd.read_excel('purchase.xlsx')
        all_data = df.to_dict(orient='records')
        return render_template('purchase.html',all_data=all_data , medname=medicine_names)

@app.route('/PSearch',methods=['POST'])
def PSearch():
    df = pd.read_excel('purchase.xlsx')
    name = request.form.get('PSearch')
    filtered_purchases = df[df['medname'] == name]
    medname = filtered_purchases.to_dict(orient='records')
    print('searched medname ',medname)
    return render_template('purchase.html',all_data = medname)

@app.route('/SSearch',methods=['POST'])
def SSearch():
    df = pd.read_excel('stock.xlsx')
    name = request.form.get('SSearch')
    filtered_purchases = df[df['Medicine'] == name]
    print(filtered_purchases)
    medname = filtered_purchases.to_dict(orient='records')
    print('searched medname ',medname)
    return render_template('stock.html',medname = medname)
@app.route('/delete', methods=['POST'])
def update():
    df = pd.read_excel('purchase.xlsx')
    selected_rows = request.form.getlist('selected_rows')
    selected_rows = [int(index) for index in selected_rows]
    # Delete the selected row(s) from the DataFrame
    df = df.drop(index=selected_rows).reset_index(drop=True)
    df.to_excel('purchase.xlsx', index=False)
    return render_template('purchase.html', all_data=df.to_dict(orient='records'))

medicine_list = []
@app.route('/billing',methods=['GET', 'POST'])
@login_required
def billing():
    df = pd.read_excel('purchase.xlsx')
    df.fillna(0, inplace=True)
    df.to_excel('purchase.xlsx', index=False)
    medicine_names = df['medname'].unique().tolist()
    if request.method == 'POST':
        cname = request.form.get('cname')
        medicin_name = request.form.get('medname')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        medicine_list.append({
            'customer_name':cname,
            'medname': medicin_name,
            'quantity': quantity,
            'price': price,
        })
        
        return render_template('billing.html',all_data=medicine_list,medname=medicine_names)
    else:
        return render_template('billing.html',medname=medicine_names)

@app.route('/generatebill',methods=['GET','POST'])
def generatebill():
    df = pd.read_excel('sales.xlsx')
    headers = ['customer_name', 'medname', 'quantity', 'price']
    df = df._append(medicine_list)
    df.to_excel('sales.xlsx', index=False)
    medicine_list.clear()
    return render_template('adminpanel.html', message='Bill generated successfully.')

@app.route('/deletebill', methods=['POST'])
def deletebill():
    selected_rows = request.form.getlist('selected_rows')
    selected_rows = [int(index) for index in selected_rows]

    # Remove selected items from medicine_list
    for index in sorted(selected_rows, reverse=True):
        if index < len(medicine_list):
            medicine_list.pop(index)

    return render_template('billing.html', all_data=medicine_list)

@app.route('/stock')
@login_required
def stock():
    purchase_df = pd.read_excel('purchase.xlsx')
    sales_df = pd.read_excel('sales.xlsx')
    purchase_totals = purchase_df.groupby('medname')['quantity'].sum().reset_index()
    sales_totals = sales_df.groupby('medname')['quantity'].sum().reset_index()
    merged_df = pd.merge(purchase_totals, sales_totals, on='medname', how='outer').fillna(0)
    merged_df['Total Count'] = merged_df['quantity_x'] - merged_df['quantity_y']
    merged_df.rename(columns={'medname': 'Medicine', 'quantity_x': 'Purchased quantity', 'quantity_y': 'Saled quantity'}, inplace=True)
    merged_df.to_excel('stock.xlsx', index=False)
    stock_data = merged_df.to_dict(orient='records')
    return render_template('stock.html',stock_data=stock_data)


@app.route('/salehistory')
@login_required
def salehis():
    df = pd.read_excel('sales.xlsx')
    sales_data = df.to_dict(orient='records')
    return render_template('salehistory.html',sales_data=sales_data)

@app.route('/search_sales', methods=['GET'])
def search_sales():
    sales_data = pd.read_excel('sales.xlsx')
    query = request.args.get('query')
    filtered_sales_data = []
    for med_details in sales_data:
        if isinstance(med_details, dict) and 'customer_name' in med_details and 'medname' in med_details:
            if query.lower() in med_details['customer_name'].lower() or query.lower() in med_details['medname'].lower():
                filtered_sales_data.append(med_details)
    return render_template('salehistory.html', sales_data=filtered_sales_data)


# @app.route('/wholesalers')
# def wholesalers():
#     return render_template('wholesalers.html')
# @app.route('/register')
# def register():
#     return render_template('register.html')
# @app.route('/changepass')
# def change():
#     return render_template('changepass.html')
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True,port=5000)
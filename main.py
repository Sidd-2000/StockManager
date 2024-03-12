from flask import Flask, render_template, request, send_file
import pandas as pd

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template('adminpanel.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/purchase',methods=['GET','POST'])
def purchase():
    df = pd.read_excel('Book1.xlsx')
    medicine_list = []
    if request.method == 'POST':
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
            df = pd.read_excel('Book1.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame()
        df = df._append(medicine_list, ignore_index=True)
        df.to_excel('Book1.xlsx', index=False)
        all_data = df.to_dict(orient='records')
        return render_template('purchase.html',all_data=all_data)
    else:
        df = pd.read_excel('Book1.xlsx')
        all_data = df.to_dict(orient='records')
        return render_template('purchase.html',all_data=all_data)

@app.route('/delete', methods=['POST'])
def update():
    df = pd.read_excel('Book1.xlsx')
    selected_rows = request.form.getlist('selected_rows')
    selected_rows = [int(index) for index in selected_rows]
    # Delete the selected row(s) from the DataFrame
    df = df.drop(index=selected_rows).reset_index(drop=True)
    df.to_excel('Book1.xlsx', index=False)
    return render_template('purchase.html', all_data=df.to_dict(orient='records'))

medicine_list = []
@app.route('/billing',methods=['GET', 'POST'])
def billing():
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
        
        return render_template('billing.html',all_data=medicine_list)
    else:
        return render_template('billing.html')

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
def stock():
    pdf = pd.read_excel('Book1.xlsx')
    sdf = pd.read_excel('sales.xlsx')
    ptotals = pdf.groupby('medname')['quantity'].sum().reset_index()
    stotals = pdf.groupby('medname')['quantity'].sum().reset_index()

    # Merge purchase and sales totals
    merged_df = pd.merge(ptotals, stotals, on='medname', how='outer').fillna(0)
    merged_df['Total Stock'] = merged_df['quantity_x'] - merged_df['quantity_y']
    merged_df[['medname', 'Total Stock']].to_excel('stock.xlsx', index=False)
    print(merged_df)
    return render_template('stock.html')


@app.route('/salehistory')
def salehis():
    return render_template('salehistory.html')


@app.route('/wholesalers')
def wholesalers():
    return render_template('wholesalers.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/changepass')
def change():
    return render_template('changepass.html')
@app.route('/logout')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True,port=5000)
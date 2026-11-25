from flask import Flask,render_template,session,request,redirect
from flask import redirect
import pymysql
app=Flask(__name__)
app.secret_key="mykey123"

def executeQuerry(sql):
    connection = pymysql.connect( host="localhost", user="root",password="root",database="blood_bank")
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()

def selectquery(sql):
    connection = pymysql.connect( host="localhost", user="root",password="root",database="blood_bank")
    cursor=connection.cursor()
    cursor.execute(sql)
    data=cursor.fetchall()
    cursor.close()
    connection.close()
    return data

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        sql = f"SELECT * FROM login WHERE username='{username}' AND password='{password}'"
        print(sql)
        data = selectquery(sql)
        if len(data) > 0:
            row = data[0]
            if row[4] == 'admin':
             session['admin_id'] = row[3]
             return render_template("admin.html")
            elif row[4] == 'donor':
                session['donor_id'] = row[3]
                return render_template("donor.html")
                return render_template("donor.html")
            elif row[4] == 'recipient':
                session['recipient_id'] = row[3]
                return render_template("recipient.html")
            else:
                return render_template(
                    "login.html",
                    error="Invalid username or password"
                )

        else:
            return render_template(
                "login.html",
                error="Invalid username or password"
            )

    return render_template("login.html")
@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/donor_register', methods=['GET', 'POST'])
def donor_register():

    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        blood_group = request.form.get('blood_group')
        last_don = request.form.get('last_don')
        username = request.form.get('username')
        password = request.form.get('password')

        if last_don == "":

            sql = f"INSERT INTO donor(name, address, gender, mobile, email, blood_group, last_don, username, password) VALUES('{name}', '{address}', '{gender}', '{mobile}', '{email}', '{blood_group}', NULL, '{username}', '{password}')"

        else:

            sql = f"INSERT INTO donor(name, address, gender, mobile, email, blood_group, last_don, username, password) VALUES('{name}', '{address}', '{gender}', '{mobile}', '{email}', '{blood_group}', '{last_don}', '{username}', '{password}')"

        executeQuerry(sql)

        sql = f"SELECT donor_id FROM donor WHERE username='{username}'"

        data = selectquery(sql)

        donor_id = data[0][0]

        sql = f"INSERT INTO login(username, password, u_id, type) VALUES('{username}', '{password}', '{donor_id}', 'donor')"

        executeQuerry(sql)
        return redirect('/login')


    return render_template("donor register.html")
 

@app.route('/donor')
def donor_dashboard():
    return render_template("donor.html")


@app.route('/donate_blood', methods=['GET', 'POST'])
def donate_blood():

    if request.method == 'POST':

        donor_id = session['donor_id']

        date = request.form.get('date')
        place = request.form.get('place')
        hospital = request.form.get('hospital')
        recipient = request.form.get('recipient')
        blood_group = request.form.get('blood_group')
        quantity = request.form.get('quantity')

        sql = f"""
        INSERT INTO donate
        (donor_id, blood_group, recipient_name, quantity,
         date_of_donation, hospital, place)
        VALUES
        ('{donor_id}', '{blood_group}', '{recipient}', '{quantity}',
         '{date}', '{hospital}', '{place}')
        """

        executeQuerry(sql)

        redirect('/donate_blood')

    return render_template("donate blood.html")

@app.route('/view_donation_history')
def donation_history():

    donor_id = session['donor_id']

    sql = f"""
   ` SELECT donor.name,
           donate.place,
           donate.hospital,
           donate.date_of_donation,
           donate.blood_group,
           donate.recipient_name,
           donate.quantity
    FROM donate
    JOIN donor
    ON donate.donor_id = donor.donor_id
    WHERE donate.donor_id = '{donor_id}'
    """

    obj = selectquery(sql)

    return render_template("view donation history.html", ob=obj)


@app.route('/view_notification')
def view_notification():
    sql = """SELECT * FROM notification  ORDER BY notification_id DESC """

    obj = selectquery(sql)

    return render_template("view notification.html", ob=obj)

@app.route('/recipient_register', methods=['GET', 'POST'])
def recipient_register():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        blood_group = request.form.get('blood_group')
        username = request.form.get('username')
        password = request.form.get('password')
        sql=f"INSERT INTO `blood_bank`.`recipient` ( `name`, `address`, `gender`, `mobile`, `email`, `blood_group`, `username`, `password`) VALUES ( '{name}', '{address}', '{gender}', '{mobile}', '{email}', '{blood_group}', '{username}', '{password}');"
        executeQuerry(sql)
        sql = f"SELECT recipient_id FROM recipient WHERE username='{username}'"
        data = selectquery(sql)
        recipient_id = data[0][0]
        sql = f"INSERT INTO login (username, password, u_id, type) VALUES('{username}','{password}','{recipient_id}','recipient')"
        executeQuerry(sql)
        return redirect('/login')
    
    return render_template("recipient register.html")


@app.route('/search_donor', methods=['GET','POST'])
def search_donor():
    obj=[]
    if request.method == 'POST':
        blood_group = request.form.get('blood_group')
        sql = f"SELECT * FROM donor WHERE blood_group='{blood_group}'"
        obj = selectquery(sql)
        # return "Searching for donors with blood group:"+blood_group

    return render_template("search donor.html",ob=obj)


@app.route('/request_blood/<int:donor_id>', methods=['GET', 'POST'])
def request_blood(donor_id):

    sql = f"SELECT * FROM donor WHERE donor_id='{donor_id}'"
    obj = selectquery(sql)

    if request.method == 'POST':

        recipient_id = session['recipient_id']

        patient_name = request.form.get('patient_name')
        blood_group = request.form.get('blood_group')
        place = request.form.get('place')
        phone_number = request.form.get('phone')

        status = 'pending'

        sql = f""" INSERT INTO request (recipient_id, patient_name, blood_group, donor_id, place, phone_number, status)  VALUES ('{recipient_id}', '{patient_name}', '{blood_group}',  '{donor_id}', '{place}', '{phone_number}', '{status}') """
        executeQuerry(sql)
        return redirect('/request_blood/' + str(donor_id))

    return render_template("request blood.html", ob=obj[0])


@app.route('/view_blood_bank')
def view_blood_bank():  
    sql="SELECT * FROM admin;"
    obj=selectquery(sql)
    return render_template("view bloodbank.html",ob=obj)


@app.route('/track_request')
def track_request():

    recipient_id = session['recipient_id']

    sql = f"""
    SELECT 
        request.patient_name,
        donor.name,
        request.blood_group,
        request.place,
        request.phone_number,
        request.status
    FROM request
    JOIN donor
        ON request.donor_id = donor.donor_id
    WHERE request.recipient_id = '{recipient_id}'
    """

    obj = selectquery(sql)

    return render_template("track request.html", ob=obj)

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():

    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        location=request.form.get('location')
        phone=request.form.get('phone')
        sql = f"INSERT INTO blood_bank.admin (name, address, gender, mobile, email, username, password, location, phone) VALUES ('{name}', '{address}', '{gender}', '{mobile}', '{email}', '{username}', '{password}', '{location}', '{phone}')"
        executeQuerry(sql)
        sql = f"SELECT admin_id FROM admin WHERE username='{username}'"
        data = selectquery(sql)
        admin_id = data[0][0]
        sql = f"INSERT INTO login (username, password, u_id, type) VALUES('{username}','{password}','{admin_id}','admin')"
        executeQuerry(sql)
        return redirect('/login')
    return render_template("admin register.html")


@app.route('/admin')
def admin_dashboard():
    return render_template("admin.html")

@app.route('/recipient')
def recipient_dashboard():
    return render_template("recipient.html")


@app.route('/manage_stock')
def manage_stock():
    admin_id = session['admin_id']
    sql = f"SELECT * FROM stock WHERE admin_id='{admin_id}'"
    obj = selectquery(sql)
    return render_template( "manage blood stock.html",ob=obj )


@app.route('/update_stock/<int:stock_id>', methods=['GET','POST'])
def update_stock(stock_id):
    admin_id = session['admin_id']
    if request.method == "POST":
        units = request.form.get('unit')
        sql = f"UPDATE stock SET units='{units}' WHERE stock_id='{stock_id}' AND admin_id='{admin_id}' "
        executeQuerry(sql)
        return redirect('/manage_stock')
    sql = f" SELECT * FROM stock WHERE stock_id='{stock_id}' AND admin_id='{admin_id}'"
    obj = selectquery(sql)
    return render_template( "update stock.html",stock=obj[0] )


@app.route('/add_stock', methods=['GET','POST'])
def add_stock():
    if request.method == 'POST':
        blood_group = request.form.get('blood_group')
        units = request.form.get('units')
        admin_id = session['admin_id']
        sql = f" INSERT INTO stock (admin_id, units, blood_group) VALUES ('{admin_id}', '{units}', '{blood_group}') "
        executeQuerry(sql)
        return redirect('/manage_stock')
    return render_template("add stock.html")
    
@app.route('/admin_view_requests')
def admin_view_requests():
    sql="SELECT *FROM request;"
    obj=selectquery(sql)
    return render_template("view request admin.html",ob=obj)


@app.route('/view_request')
def view_request():
    donor_id = session['donor_id']
    sql = f"""SELECT * FROM request WHERE donor_id = '{donor_id}' """
    obj = selectquery(sql)
    return render_template("view request.html", ob=obj)

@app.route('/accept_request/<int:request_id>')
def accept_request(request_id):

    sql = f"UPDATE request SET status='Accepted' WHERE request_id='{request_id}'"

    executeQuerry(sql)

    return redirect('/view_request')

@app.route('/reject_request/<int:request_id>')
def reject_request(request_id):

    sql = f"UPDATE request SET status='Rejected' WHERE request_id='{request_id}'"

    executeQuerry(sql)

    return redirect('/view_request')


@app.route('/post_notification', methods=['GET','POST'])
def post_notification():

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        sql=f"INSERT INTO `blood_bank`.`notification` ( `title`, `description`) VALUES ( '{title}', '{description}');"
        executeQuerry(sql)
        redirect('/post_notification')

    return render_template("send notification.html")


if __name__=='__main__':
    app.run(debug=True)

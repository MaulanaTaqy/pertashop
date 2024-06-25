from flask import Flask,redirect,url_for, render_template, jsonify, request, session, flash 
from pymongo import MongoClient,DESCENDING
from bson import ObjectId
from datetime import datetime
import locale

client = MongoClient('mongodb+srv://maulanataqy99:sparta@taqy.64czrl4.mongodb.net/')
db = client.pertashop

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

@app.template_filter('rupiah')
def rupiah_format(value):
    try:
        formatted_value = locale.currency(value, grouping=True)
        # Removing the space between the symbol and the value
        return formatted_value.replace('Rp', 'Rp. ')
    except Exception as e:
        return value

app.jinja_env.filters['rupiah'] = rupiah_format

@app.route('/',methods=['GET','POST'])
def home():
    
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = db.user.find_one({'username': username, 'password': password})
        if user_data:
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            flash('Logged in successfully!', 'success')
            if user_data['role'] == 'admin':
                return redirect(url_for('admin'))
            elif user_data['role'] == 'user':
                return redirect(url_for('pegawai'))
        flash('Invalid username or password', 'danger')
     return render_template('login.html')
    


### START ADMIN ###

@app.route('/admin',methods=['GET','POST'])
def admin():
    if 'username' in session and session.get('role') == 'admin':
       
        ##PEMASUKAN
        pemasukan_entries = list(db.pemasukan.find({}, {'_id': 0, 'pemasukan': 1, 'tanggal': 1}))
        total_pemasukan = sum(float(entry['pemasukan']) for entry in pemasukan_entries if 'pemasukan' in entry)
        formatted_rupiah_pemasukan = format_rupiah(total_pemasukan)

        ##PENGELUARAN
        pengeluaran_entries = list(db.pengeluaran.find({}, {'_id': 0, 'pengeluaran': 1, 'tanggal': 1}))
        total_pengeluaran = sum(float(entry['pengeluaran']) for entry in pengeluaran_entries if 'pengeluaran' in entry)
        formatted_rupiah_pengeluaran = format_rupiah(total_pengeluaran)
        
        ##PENDAPATAN   
        pendatapan = format_rupiah(total_pemasukan-total_pengeluaran)
        
        ##PEMASUKAN PER BULAN
        monthly_pemasukan = [0] * 12
        pemasukan_entries = list(db.pemasukan.find({}, {'_id': 0, 'pemasukan': 1, 'tanggal': 1}))
        
        
        for entry in pemasukan_entries:
            try:
                month_index = datetime.strptime(entry['tanggal'], '%Y-%m-%d').month - 1  
                monthly_pemasukan[month_index] += float(entry['pemasukan'])
            except ValueError:
                
                pass

        
        
        stok =  list(db.stok.find({}))
        
        return render_template('admin/adminPage.html',stok=stok,monthly_pemasukan=monthly_pemasukan,
                            total_pemasukan=formatted_rupiah_pemasukan,
                            total_pengeluaran=formatted_rupiah_pengeluaran,
                            pendapatan=pendatapan
                            )
    return redirect(url_for('login'))
@app.route('/pemasukan',methods=['GET','POST'])
def pemasukan():
      ##PEMASUKAN
    if 'username' in session and session.get('role') == 'admin':
        pemasukan_entries = list(db.pemasukan.find({}, {'_id': 0, 'pemasukan': 1, 'tanggal': 1}))
        total_pemasukan = sum(float(entry['pemasukan']) for entry in pemasukan_entries if 'pemasukan' in entry)
        formatted_rupiah_pemasukan = format_rupiah(total_pemasukan)
    
        pemasukan =  list(db.pemasukan.find({}))
        return render_template('admin/detailPemasukan.html',pemasukan=pemasukan,total_pemasukan=formatted_rupiah_pemasukan)
    return redirect(url_for('login'))
@app.route('/editPemasukan/<_id>',methods=['GET','POST'])
def editPemasukan(_id):
    if 'username' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            id = request.form['_id']
            pemasukan = float(request.form['pemasukan'])
            tanggal = request.form['tanggal']
            detail = request.form['detail']

        
            
            doc = {
                'pemasukan' : pemasukan,
                'tanggal' : tanggal,
                'detail' : detail
            }
            db.pemasukan.update_one({"_id":ObjectId(id)},{'$set' : doc})
            return redirect(url_for('pemasukan'))
        id = ObjectId(_id)
        data = list(db.pemasukan.find({'_id':id}))
        return render_template('admin/editPemasukan.html',data=data)
    return redirect(url_for('login'))


@app.route('/deletePemasukan/<_id>',methods=['GET','POST'])
def deletepemasukan(_id):
    if 'username' in session and session.get('role') == 'admin':
        db.pemasukan.delete_one({'_id' : ObjectId(_id)})
        return redirect(url_for('pemasukan'))
    return redirect(url_for('login'))

@app.route('/pengeluaran',methods=['GET','POST'])
def pengeluaran():
    if 'username' in session and session.get('role') == 'admin':
        pengeluaran_entries = list(db.pengeluaran.find({}, {'_id': 0, 'pengeluaran': 1, 'tanggal': 1}))
        total_pengeluaran = sum(float(entry['pengeluaran']) for entry in pengeluaran_entries if 'pengeluaran' in entry)
        formatted_rupiah_pengeluaran = format_rupiah(total_pengeluaran)
        
        pengeluaran =  list(db.pengeluaran.find({}))
        return render_template('admin/detailPengeluaran.html',pengeluaran=pengeluaran,total_pengeluaran=formatted_rupiah_pengeluaran)
    return redirect(url_for('login'))
@app.route('/editPengeluaran/<_id>',methods=['GET','POST'])
def editpengeluaran(_id):
    if 'username' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            id = request.form['_id']
            pengeluaran = float(request.form['pengeluaran'])
            tanggal = request.form['tanggal']
            detail = request.form['detail']

        
            
            doc = {
                'pengeluaran' : pengeluaran,
                'tanggal' : tanggal,
                'detail' : detail
            }
            db.pengeluaran.update_one({"_id":ObjectId(id)},{'$set' : doc})
            return redirect(url_for('pengeluaran'))
        id = ObjectId(_id)
        data = list(db.pengeluaran.find({'_id':id}))
        return render_template('admin/editPengeluaran.html',data=data)
    return redirect(url_for('login'))
@app.route('/deletePengeluaran/<_id>',methods=['GET','POST'])
def deletePengeluaran(_id):
    if 'username' in session and session.get('role') == 'admin':
        db.pengeluaran.delete_one({'_id' : ObjectId(_id)})
        return redirect(url_for('pengeluaran'))
    return redirect(url_for('login'))


@app.route('/inputPengeluaran',methods=['GET','POST'])
def inputPengeluaran():
    if 'username' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            pengeluaran = float(request.form['pengeluaran'])
            tanggal = request.form['tanggal']
            detail = request.form['detail']
            
            
            doc = {
                'pengeluaran' : pengeluaran,
                'tanggal' : tanggal,
                'detail' : detail,     
            }
            db.pengeluaran.insert_one(doc)
            return redirect(url_for('admin'))
        
        return render_template('admin/inputPengeluaran.html')
    return redirect(url_for('login'))
@app.route('/stok',methods=['GET','POST'])
def stok():
    if 'username' in session and session.get('role') == 'admin':
        stok =  list(db.stok.find({}))
        return render_template('admin/detailstok.html',stok=stok)
    return redirect(url_for('login'))

@app.route('/editStok/<_id>',methods=['GET','POST'])
def editStok(_id):
    if 'username' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            id = request.form['_id']
            stok_awal = request.form['stok_awal']
            stok_akhir = request.form['stok_akhir']
            tanggal = request.form['tanggal']

        
            
            doc = {
                'stok_awal' : stok_awal,
                'stok_akhir' : stok_akhir,
                'tanggal' : tanggal
            }
            db.stok.update_one({"_id":ObjectId(id)},{'$set' : doc})
            return redirect(url_for('stok'))
        id = ObjectId(_id)
        data = list(db.stok.find({'_id':id}))
        return render_template('admin/editStok.html',data=data)
    return redirect(url_for('login'))


@app.route('/deleteStok/<_id>',methods=['GET','POST'])
def deleteStok(_id):
    if 'username' in session and session.get('role') == 'admin':
        db.stok.delete_one({'_id' : ObjectId(_id)})
        return redirect(url_for('stok'))
    return redirect(url_for('login'))


@app.route('/register',methods=['GET','POST'])
def register():
    if 'username' in session and session.get('role') == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            
            
            doc = {
                'username' : username,
                'password' : password,
                'role' : "user",     
            }
            db.user.insert_one(doc)
            return redirect(url_for('admin'))
        return render_template('admin/registerPegawai.html')
    return redirect(url_for('login'))

###  END ADMIN  ####


###  START PEGAWAI  ####
def format_rupiah(amount):
    return "Rp. {:,.2f}".format(amount).replace(",", ".").replace(".", ",")

@app.route('/pegawai',methods=['GET','POST'])
def pegawai():
    if 'username' in session and session.get('role') == 'user':
        pemasukan_entries = list(db.pemasukan.find({}, {'_id': 0, 'pemasukan': 1, 'tanggal': 1}))
        total_pemasukan = sum(float(entry['pemasukan']) for entry in pemasukan_entries if 'pemasukan' in entry)
        formatted_rupiah = format_rupiah(total_pemasukan)
        pemasukan =  list(db.pemasukan.find({}))
        return render_template('pegawai/employeePage.html', pemasukan=pemasukan,total_pemasukan=formatted_rupiah)
    return redirect(url_for('login'))


@app.route('/inputPemasukan',methods=['GET','POST'])
def inputPemasukan():
     if 'username' in session and session.get('role') == 'user':
        if request.method == 'POST':
            pemasukan = float(request.form['pemasukan'])
            tanggal = request.form['tanggal']
            detail = request.form['detail']
            
            
            doc = {
                'pemasukan' : pemasukan,
                'tanggal' : tanggal,
                'detail' : detail,     
            }
            db.pemasukan.insert_one(doc)
            return redirect(url_for('pegawai'))
        
        return render_template('pegawai/inputPemasukan.html')
     return redirect(url_for('login'))
 
 
@app.route('/inputStok',methods=['GET','POST'])
def inputStok():
    if 'username' in session and session.get('role') == 'user':
      if request.method == 'POST':
        stok_awal = request.form['stok_awal']
        stok_akhir = request.form['stok_akhir']
        tanggal = request.form['tanggal']
        
        doc = {
            'stok_awal' : stok_awal,
            'stok_akhir' : stok_akhir,
            'tanggal' : tanggal,     
        }
        db.stok.insert_one(doc)
        return redirect(url_for('pegawai'))
    
      return render_template('pegawai/inputStok.html')
    return redirect(url_for('login'))
###  END PEGAWAI  ####

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
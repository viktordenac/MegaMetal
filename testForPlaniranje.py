from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database_name.db'
db = SQLAlchemy(app)

class YourTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Kupec = db.Column(db.String)
    Predlozeni_datum_zbiranja = db.Column(db.Date)
    Opombe = db.Column(db.String)
    Nalog = db.Column(db.String(10))
    IDENT_NR = db.Column(db.Integer)
    Index = db.Column(db.String)
    Barva = db.Column(db.String)
    KOS_st = db.Column(db.Integer)
    KOS_num = db.Column(db.Integer)
    Zbiranje_DO = db.Column(db.Date)
    SastavljenjeOD = db.Column(db.Date)
    SastavljenjeDO = db.Column(db.Date)
    Sastavljenjedani = db.Column(db.Integer)
    STATUS_sastavljenje = db.Column(db.Integer)
    VarenjeOD = db.Column(db.Date)
    VarenjeDO = db.Column(db.Date)
    Varenjedani = db.Column(db.Integer)
    STATUS_varenje = db.Column(db.Integer)
    ZarenjeOD = db.Column(db.Date)
    ZarenjeDO = db.Column(db.Date)
    Zarenjedani = db.Column(db.Integer)
    Spremno_za_isporuku = db.Column(db.Date)
    STATUS_isporuka = db.Column(db.Integer)
    Dejanski_datum_isporuke = db.Column(db.Date)
    Confirmed_delivery_date = db.Column(db.Date)
    Year = db.Column(db.Integer)

    def __repr__(self):
        return f"<YourTable {self.id}>"


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

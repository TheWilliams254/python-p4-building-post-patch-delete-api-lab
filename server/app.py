#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries', methods=['GET'])
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return jsonify(bakeries), 200

@app.route('/bakeries/<int:id>', methods=['GET'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    return jsonify(bakery.to_dict()), 200

@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return jsonify([bg.to_dict() for bg in baked_goods]), 200

@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    bg = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not bg:
        return jsonify({'error': 'No baked goods found'}), 404
    return jsonify(bg.to_dict()), 200

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'GET':
        baked_goods = BakedGood.query.all()
        return jsonify([bg.to_dict() for bg in baked_goods]), 200
    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_bg = BakedGood(
                name=data['name'],
                price=data['price'],
                bakery_id=data['bakery_id']
            )
            db.session.add(new_bg)
            db.session.commit()
            return jsonify(new_bg.to_dict()), 201
        except KeyError:
            return jsonify({'error': 'Missing data fields'}), 400

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    data = request.get_json()
    bakery.name = data.get('name', bakery.name)
    db.session.commit()
    return jsonify(bakery.to_dict()), 200

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return jsonify({'error': 'Baked good not found'}), 404
    db.session.delete(bg)
    db.session.commit()
    return jsonify({'message': 'Baked good deleted'}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)

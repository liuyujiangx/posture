from . import admin
from flask import render_template, request, jsonify


@admin.route('/')
def article():
    print("hello")
    return render_template('index.html')

@admin.route('/article/delete/')
def article_delete():
    data = request.form.to_dict()
    print(data)
    return jsonify('dad')
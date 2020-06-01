from . import admin
from flask import render_template, request, jsonify


@admin.route('/')
def index():
    print("hello")
    return render_template('index.html')

@admin.route('/article/')
def article():
    return render_template('article.html')


@admin.route('/article/delete/')
def article_delete():
    data = request.form.to_dict()
    print(data)
    return jsonify('dad')
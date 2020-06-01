from . import admin
from flask import render_template, request, jsonify


@admin.route('/article/')
def article():
    print("hello")
    return render_template('article.html')

@admin.route('/article/delete/')
def article_delete():
    data = request.form.to_dict()
    print(data)
    return jsonify('dad')
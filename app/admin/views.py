import json

from app import db
from app.models import Article, Spotsite, Comment
from . import admin
from flask import render_template, request, jsonify


@admin.route('/')
def index():
    print("hello")
    return render_template('index.html')

@admin.route('/article/')
def article():
    return render_template('article.html')
@admin.route('/comment/')
def comment():
    return render_template('comment.html')

@admin.route('/spotsite/')
def spotsite():
    return render_template('spotsite.html')
@admin.route('/user/')
def user():
    return render_template('user.html')

@admin.route('/article/delete/',methods=['POST'])
def article_delete():
    data = request.get_data()
    data = json.loads(data)
    for i in data["data"]:
        article = Article.query.filter_by(id=i["id"]).first()
        comment_list = Comment.query.filter_by(articleid = article.id).all()
        for comment in comment_list:
            db.session.delete(comment)
            db.session.commit()
        db.session.delete(article)
        db.session.commit()

    return jsonify({
        "code":1,
        "info":"删除成功"
    })

@admin.route('/spotsite/add/',methods=['POST'])
def apotsite_add():
    data = request.form.to_dict()
    spotsite = Spotsite(
        id = data["id"],
        name = data["name"]
    )
    db.session.add(spotsite)
    db.session.commit()
    return jsonify({
        "code":1,
        "info":"添加成功"
    }
    )


@admin.route('/spotsite/delete/',methods=['POST'])
def apotsite_del():
    data = request.get_data()
    data = json.loads(data)
    for i in data["data"]:
        spotsite = Spotsite.query.filter_by(id=i["id"]).first()
        db.session.delete(spotsite)
        db.session.commit()
    return jsonify({
        "code":1,
        "info":"删除成功"
    }
    )
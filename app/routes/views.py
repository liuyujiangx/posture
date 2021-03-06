import datetime
import json
import os
import uuid
from app.routes.posenet.test import Pose
from threading import Thread
from PIL import Image
from flask import request, jsonify
from sqlalchemy import text
from app import db, app
from app.models import User, Article, Spotsite, Comment

from app.routes.login import Login
from app.routes.createId import IdWorker
from app.routes.img_zoom import zoom
from . import home


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@home.route('/')
def index():
    return 'hello'


log = Login()

idword = IdWorker()


@home.route('/login/', methods=['GET'])
def login():
    res = request.args.to_dict()
    log.set(res['code'])
    openid = log.sent_out()
    usercount = User.query.filter_by(uuid=openid['openid']).count()
    if usercount != 1:  # 如果当前用户没有登录过就存进数据库
        user = User(
            username=res['userName'],
            face=res['userUrl'],
            money=0,
            uuid=openid['openid']
        )
        db.session.add(user)
        db.session.commit()
    return jsonify({"isLogin": "ture", "openid": openid['openid']})


pose = Pose()


# 获得姿势
@home.route('/posenet/', methods=["POST"])
def posenet():
    img = request.files["imgfile"]
    imgname = change_filename(img.filename)  # 更改名称
    img.save(app.config["UP_DIR"] + "upload/" + imgname)
    zoom(app.config["UP_DIR"] + "upload/" + imgname, app.config["UP_DIR"] + "upload/" + imgname)  # 压缩图片
    dic = pose.pose(app.config["UP_DIR"] + "upload/" + imgname,
                    app.config["UP_DIR"] + "upload/" + "posture" + imgname)  # 调用姿势文件
    return jsonify({
        "dic": dic,
        "img_url": "http://www.yujl.top:5052/upload/" + imgname,
        "pose_url": "http://www.yujl.top:5052/upload/" + "posture" + imgname
    })


# 文章上传
@home.route('/article/upload/', methods=['POST'])
def article_upload():
    img = request.files['imgfile']
    img_filename = change_filename(img.filename)  # 更改图片名称
    save_url = app.config["UP_DIR"] + "upload/" + img_filename  # 图片保存地址
    img.save(save_url)  # 保存图片
    zoom(save_url, save_url)  # 压缩图片
    data = request.form.to_dict()
    user = User.query.filter_by(uuid=data['userid']).first()
    dic = {}
    if int(data['isPose']) == 1:  # 判断是否需要姿势点
        dic = pose.pose(save_url, app.config["UP_DIR"] + "upload/" + "posture" + img_filename)
    article = Article(
        title=data["title"],
        content=data["content"],
        spotid=data["spotid"],
        img="http://www.yujl.top:5052/upload/" + img_filename,
        postpoint=str(dic),
        weather=data["weather"],
        userid=user.id,
        good=0,
        time=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        keyword=data["keyword"],
        poseimg="http://www.yujl.top:5052/upload/" + "posture" + img_filename
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"code": 1})


# 无图文章上传
@home.route('/article/add/', methods=['POST'])
def article_add():
    data = request.get_data()
    data = json.loads(data)
    user = User.query.filter_by(uuid=data['userid']).first()
    article = Article(
        title=data["title"],
        content=data["content"],
        spotid=data["spotid"],
        img=data["img"],
        poseimg=data["poseimg"],
        postpoint=str(data["postpoint"]),
        weather=data["weather"],
        userid=user.id,
        good=0,
        time=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        keyword=data["keyword"]
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"code": 1})


# 添加评论
@home.route("/add/comment/", methods=["POST"])
def add_comment():
    data = request.get_data()
    data = json.loads(data)
    user = User.query.filter_by(uuid=data["userid"]).first()
    comment = Comment(
        content=data["content"],
        articleid=data["articleid"],
        userid=user.id,
        time=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        read=0,
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"code": 1})


@home.route('/get/comment/')
def get_comment():
    data = request.args.to_dict()
    if len(data) == 2 or len(data) == 4:  # 后台管理用的返回值
        comment = Comment.query.order_by(Comment.id.asc()).paginate(page=int(data["page"]),
                                                                    per_page=int(data["limit"]))
    elif len(data) == 3:  # 小程序用的返回值
        count = Comment.query.filter_by(articleid=data["articleid"]).count()
        if (int(data["page"]) - 1) * int(data["limit"]) + 1 > count:  # 请求的页数超过数据量就返回空数组
            return jsonify({
                "code": 0,
                "msg": "获取评论",
                "count": count,
                "data": []
            })
        comment = Comment.query.filter_by(articleid=data["articleid"]).order_by(Comment.id.desc()).paginate(
            page=int(data["page"]),
            per_page=int(data["limit"]))
    else:
        comment = Comment.query.paginate(page=1, per_page=100)
    commentcount = Comment.query.count()

    return jsonify(
        {
            "code": 0,
            "msg": "获取评论",
            "count": commentcount,
            "data": [
                {"id": item.id, "time": item.time, "content": item.content, "article": item.article.title,
                 "username": item.user.username, "userimg": item.user.face,"read":item.read } for item in comment.items
            ]
        }
    )


# 获取文章
@home.route('/get/article/')
def get_article():
    data = request.args.to_dict()
    if len(data) == 0:
        data["page"] = 1
        data["limit"] = 10
    articlecount = Article.query.count()
    if (int(data["page"]) - 1) * int(data["limit"]) + 1 > articlecount:
        return jsonify({
            "code": 0,
            "msg": "获取文章",
            "count": articlecount,
            "data": []
        })
    article = Article.query.order_by(Article.id.desc()).paginate(page=int(data["page"]), per_page=int(data["limit"]))
    return jsonify(
        {
            "code": 0,
            "msg": "获取文章",
            "count": articlecount,
            "data": [
                {"id": item.id, "title": item.title, "content": item.content, "img": item.img, "keyword": item.keyword,
                 "spotid": item.spotsite.name, "userid": item.user.username, "good": item.good, "weather": item.weather,
                 "poseimg": item.poseimg, "userimg": item.user.face,"rewardurl":item.user.rewardurl,
                 "postpoint": item.postpoint, "scaling": item.scaling, "time": item.time} for item in article.items
            ]
        }
    )


# 获取景点
@home.route('/get/spotsite/')
def get_spotsite():
    data = request.args.to_dict()
    if len(data) == 0:  # 小程序按分类获取景点或地点
        province = Spotsite.query.filter(text("SUBSTR(id,3,6) = 0 ")).all()
        city = Spotsite.query.filter(text("SUBSTR(id,3,4) != 0 and SUBSTR(id,5,6)=0")).all()
        spot = Spotsite.query.filter(text("SUBSTR(id,5,6) != 0 ")).all()
        spot_data = {}
        city_data = {}
        province_data = {}
        for i in province:
            province_data[i.id] = i.name
        for i in spot:
            spot_data[i.id] = i.name
        for i in city:
            city_data[i.id] = i.name
        return jsonify({
            "code": 0,
            "msg": "获取景点",
            "province": province_data,
            "city": city_data,
            "spot": spot_data,
            })
    spotsite = Spotsite.query.order_by(Spotsite.id.asc()).paginate(page=int(data["page"]), per_page=int(data["limit"]))
    spotsitecount = Spotsite.query.count()
    return jsonify(
        {
            "code": 0,
            "msg": "获取景点",
            "count": spotsitecount,
            "data": [
                {"id": item.id, "name": item.name} for item in spotsite.items
            ],

        }
    )


# 获取用户
@home.route('/get/user/')
def get_user():
    data = request.args.to_dict()
    if len(data) == 0:
        data["page"] = 1
        data["limit"] = 10
    user = User.query.order_by(User.id.asc()).paginate(page=int(data["page"]), per_page=int(data["limit"]))
    usercount = User.query.count()
    return jsonify(
        {
            "code": 0,
            "msg": "获取用户",
            "count": usercount,
            "data": [
                {"id": item.id, "username": item.username, "uuid": item.uuid,
                 "face": item.face, "money": item.money, "rewardurl": item.rewardurl} for item in user.items
            ]
        }
    )


# 点赞
@home.route('/good/')
def good():
    data = request.args.to_dict()
    article = Article.query.filter_by(id=data["id"]).first()
    article.good += 1
    db.session.add(article)
    db.session.commit()
    return jsonify({"good": article.good, "msg": "点赞成功"})


# 搜索
@home.route('/search/')
def search():
    data = request.args.to_dict()
    data = data['data']
    article_title = Article.query.filter(
        Article.title.like("%" + data + "%") if data is not None else "").all()  # 跟标题相关的
    article_keyword = Article.query.filter(
        Article.keyword.like("%" + data + "%") if data is not None else "").all()  # 跟关键词相关的
    article_weather = Article.query.filter(
        Article.weather.like("%" + data + "%") if data is not None else "").all()  # 跟天气相关的
    spotsite = Spotsite.query.filter(Spotsite.name.like("%" + data + "%") if data is not None else "").first()  # 查询地点
    s = set()
    for i in article_title:
        s.add(i)
    for i in article_keyword:
        s.add(i)
    for i in article_weather:
        s.add(i)
    if spotsite:
        item = Article.query.filter_by(spotid=spotsite.id).all()
        if item is not None:
            for i in item:
                s.add(i)
    res = [
        {"id": item.id, "title": item.title, "content": item.content, "img": item.img, "keyword": item.keyword,
         "spotid": item.spotsite.name, "userid": item.user.username, "good": item.good, "weather": item.weather,
         "poseimg": item.poseimg, "userimg": item.user.face,"rewardurl":item.user.rewardurl,
         "postpoint": item.postpoint, "scaling": item.scaling, "time": item.time} for item in s
    ]

    return jsonify(
        {
            "code": 0,
            "msg": "搜索文章",
            "data": res

        }
    )


# 按天气分类获取文章
@home.route('/get/weather/')
def get_weather():
    data = request.args.to_dict()
    article = Article.query.filter_by(weather=data["weather"]).all()
    return jsonify(
        {
            "code": 0,
            "msg": "按天气获取文章",
            "data": [
                {"id": item.id, "title": item.title, "content": item.content, "img": item.img, "keyword": item.keyword,
                 "spotid": item.spotsite.name, "userid": item.user.username, "good": item.good, "weather": item.weather,
                 "poseimg": item.poseimg, "userimg": item.user.face,"rewardurl":item.user.rewardurl,
                 "postpoint": item.postpoint, "scaling": item.scaling, "time": item.time} for item in article
            ]
        }
    )


@home.route('/user/article/')
def user_article():
    data = request.args.to_dict()
    user = User.query.filter_by(uuid=data["userid"]).first()
    article = Article.query.filter_by(userid=user.id).all()
    return jsonify(
        {
            "code": 0,
            "msg": "按用户获取文章",
            "data": [
                {"id": item.id, "title": item.title, "content": item.content, "img": item.img, "keyword": item.keyword,
                 "spotid": item.spotsite.name, "userid": item.user.username, "good": item.good, "weather": item.weather,
                 "poseimg": item.poseimg, "userimg": item.user.face,"rewardurl":item.user.rewardurl,
                 "postpoint": item.postpoint, "scaling": item.scaling, "time": item.time} for item in article
            ]
        }
    )


@home.route('/article/delete/')
def article_del():
    data = request.args.to_dict()
    article = Article.query.filter_by(id=data["articleid"]).first()
    comment_list = Comment.query.filter_by(articleid=article.id).all()
    for comment in comment_list:
        db.session.delete(comment)
        db.session.commit()
    db.session.delete(article)
    db.session.commit()
    return jsonify({
        "code": 1,
        "info": "删除成功"
    })


@home.route('/article/update/', methods=["POST"])
def article_update():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    article = data["article"]
    spotsite = Spotsite.query.filter_by(name=article["spotname"]).first()
    articles = Article.query.filter_by(id=article['id']).first()
    articles.title = article['title']
    articles.content = article['content']
    articles.keyword = article['keyword']
    articles.weather = article['weather']
    articles.spotid = spotsite.id
    db.session.add(articles)
    db.session.commit()
    return jsonify(data)


# 获取该用户所有文章的评论
@home.route('/user/comment/')
def user_comment():
    data = request.args.to_dict()
    user = User.query.filter_by(uuid=data['userid']).first()
    article = Article.query.filter_by(userid=user.id).all()
    ls = []
    for i in article:
        comment = Comment.query.filter_by(articleid=i.id).order_by(Comment.read.asc()).all()
        for j in comment:
            ls.append(j)
    res = [
        {"id": item.id, "time": item.time, "content": item.content, "article": item.article.title,
         "username": item.user.username, "userimg": item.user.face, "read": item.read} for item in ls
    ]
    res = sorted(res, key=lambda item: (item['read'], -item['id']))  # 未读在前面然后按时间排序
    return jsonify(
        {
            "code": 0,
            "msg": "获取该用户所有文章的评论",
            "data": res
        }
    )


# 已读评论
@home.route('/read/comment/', methods=["POST"])
def read_comment():
    data = request.get_data()
    data = json.loads(data)
    for i in data["data"]:
        comment = Comment.query.filter_by(id=i).first()
        comment.read = 1
        db.session.add(comment)
        db.session.commit()
    return jsonify({
        "code": 1,
        "msg": "点击已读评论"
    })


# 获取该用户所有文章评论未读数量
@home.route('/unread/')
def unread():
    data = request.args.to_dict()
    user = User.query.filter_by(uuid=data['userid']).first()
    article = Article.query.filter_by(userid=user.id).all()
    count = 0
    for i in article:
        comment = Comment.query.filter(Comment.articleid == i.id, Comment.read == 0).count()
        count += comment
    return jsonify({
        "code": 1,
        "unread": count
    })


@home.route('/qr/upload/', methods=['POST'])
def qr_upload():
    img = request.files['imgfile']
    data = request.form.to_dict()
    if img is not None and data is not None:
        user = User.query.filter_by(uuid=data["userid"]).first()
        img_filename = change_filename(img.filename)  # 更改图片名称
        img_filename = str(user.id) + "-" + img_filename
        save_url = app.config["UP_DIR"] + "upload/" + img_filename  # 图片保存地址
        img.save(save_url)  # 保存图片
        user.rewardurl = "http://www.yujl.top:5052/upload/" + img_filename
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "code": 1,
            "msg": "添加成功"
        })
    return jsonify({
        "code": -1,
        "msg": "请求数据为空"
    })


@home.route('/get/qr/')
def get_qr():
    data = request.args.to_dict()
    user = User.query.filter_by(uuid=data['userid']).first()
    if user.rewardurl is None:
        return jsonify({})
    return jsonify({
        "reward": user.rewardurl
    })






'''
{'article': {'title': '洛带古镇打卡', 'content': '古老的城楼古堡是个打卡的好地方
,欢迎评论交流', 'keyword': '站立', 'spotname': '欢乐谷', 'weather': '晴天', 'use
rid': 'ov7vI5SY49ssAlJU32azqnLQAgfw'}}
'''

# 多线程
# def async_slow_function(file_path, filename, num):
#     thr = Thread(target=change, args=[file_path, filename, num])
#     thr.start()
#     return thr

import datetime
import json
import os
import uuid
from app.routes.posenet.test import Pose
from threading import Thread
from PIL import Image
from flask import request, jsonify

from app import db, app
from app.models import User, Article, Spotsite

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
    if usercount != 1:
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
    imgname = change_filename(img.filename)
    img.save(app.config["UP_DIR"] + "upload/" + imgname)
    zoom(app.config["UP_DIR"] + "upload/" + imgname, app.config["UP_DIR"] + "upload/" + imgname)  # 压缩图片
    dic = pose.pose(app.config["UP_DIR"]+ "upload/" + imgname, app.config["UP_DIR"] + "upload/" + "posture" + imgname)
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
        time=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        keyword=data["keyword"],
        poseimg = "http://www.yujl.top:5052/upload/"+ "posture" + img_filename
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"code": 1})

# 文章上传
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
        time=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        keyword=data["keyword"]
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"code": 1})





# 获取文章
@home.route('/get/article/')
def get_article():
    data = request.args.to_dict()
    if len(data) == 0:
        data["page"] = 1
        data["limit"] = 10
    article = Article.query.order_by(Article.id.asc()).paginate(page=int(data["page"]), per_page=int(data["limit"]))
    articlecount = Article.query.count()
    return jsonify(
        {
            "code": 0,
            "msg": "获取文章",
            "count": articlecount,
            "data": [
                {"id": item.id, "title": item.title, "content": item.content, "img": item.img, "keyword": item.keyword,
                 "spotid": item.spotsite.name, "userid": item.user.username, "good": item.good, "weather": item.weather,
                 "poseimg": item.poseimg,
                 "postpoint": item.postpoint, "scaling": item.scaling, "time": item.time} for item in article.items
            ]
        }
    )

# 获取景点
@home.route('/get/spotsite/')
def get_spotsite():
    data = request.args.to_dict()
    if len(data) == 0:
        data["page"] = 1
        data["limit"] = 10
    spotsite = Spotsite.query.order_by(Spotsite.id.asc()).paginate(page=int(data["page"]), per_page=int(data["limit"]))
    spotsitecount = Spotsite.query.count()
    return jsonify(
        {
            "code": 0,
            "msg": "获取景点",
            "count": spotsitecount,
            "data": [
                {"id": item.id, "name": item.name} for item in spotsite.items
            ]
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
            "msg": "获取景点",
            "count": usercount,
            "data": [
                {"id": item.id, "username": item.username,"uuid":item.uuid,"face":item.face,"money":item.money} for item in user.items
            ]
        }
    )

# 多线程
# def async_slow_function(file_path, filename, num):
#     thr = Thread(target=change, args=[file_path, filename, num])
#     thr.start()
#     return thr

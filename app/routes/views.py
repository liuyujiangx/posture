import datetime
import os
import uuid
from app.routes.posenet.test import Pose
from threading import Thread
from PIL import Image
from flask import request, jsonify

from app import db, app
from app.models import User, Article

from app.routes.login import Login
from app.routes.createId import IdWorker
from app.routes.img_zoom import zoom
from . import home


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    print(datetime.datetime.now().strftime("%Y%m%d"))
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


@home.route('/posenet/', methods=["POST"])
def posenet():
    img = request.files["imgfile"]
    img.save(app.config["UP_DIR"] + img.filename)
    dic = pose.pose(app.config["UP_DIR"] + img.filename)
    return jsonify(dic)


@home.route('/article/upload/', methods=['POST'])
def article_upload():
    img = request.files['imgfile']
    img_filename = change_filename(img.filename)  # 更改图片名称
    save_url = app.config["UP_DIR"] + "upload/" + img_filename  # 图片保存地址
    img.save(save_url)  # 保存图片
    zoom(save_url, save_url)  # 压缩图片
    data = request.form.to_dict()
    user = User.query.filter_by(uuid=data['userid']).first()
    dic = {"arr": ""}
    if data['isPose']:  # 判断是否需要姿势点
        dic = pose.pose(app.config["UP_DIR"] + img.filename)
    article = Article(
        title=data["title"],
        content=data["content"],
        spotid=data["spotid"],
        img="http://www.yujl.top:5052/upload/" + img_filename,
        postpoint=dic["arr"],
        weather=data["weather"],
        userid=user.id,
        good=0,
        time=datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({"code": 1})


'''
{'title': 'awdawd', 'content': 'awfdawd', 'isPose': '[object Boolean]', 'spotid'
: '110101', 'posepoint': '[object Null]', 'weather': '[object Object]', 'userid'
: 'ov7vI5SY49ssAlJU32azqnLQAgfw'}

'''


# 获取文件大小（KB）
def get_img_kb(filePath):
    # filePath图片地址（包含图片本身）
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024)

    return round(fsize, 2)


# 对图片进行压缩处理,w>512=>512
def img_compress(from_src, save_src):
    # from_src需要压缩的图片地址,save_src压缩后图片的保存地址。（地址中包含图片本身）
    img = Image.open(from_src)
    w, h = img.size
    if w > 512:
        h = h * (512 / w)
        w = w * (512 / w)

    img = img.resize((int(w), int(h)), Image.ANTIALIAS)
    img.save(save_src, optimize=True, quality=85)  # 质量为85效果最好
    if get_img_kb(save_src) > 60:
        img.save(save_src, optimize=True, quality=75)

# 多线程
# def async_slow_function(file_path, filename, num):
#     thr = Thread(target=change, args=[file_path, filename, num])
#     thr.start()
#     return thr

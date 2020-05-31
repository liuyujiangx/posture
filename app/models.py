from app import db


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)  # 文章标题
    content = db.Column(db.String)  # 文章内容
    img = db.Column(db.String)  # 图片地址
    keyword = db.Column(db.String)  # 关键词
    spotid = db.Column(db.Integer)
    userid = db.Column(db.Integer)
    good = db.Column(db.Integer)  # 点赞数
    weather = db.Column(db.String)  # 天气
    poseimg = db.Column(db.String)  #
    postpoint = db.Column(db.String)  # 姿势点
    scaling = db.Column(db.String)  # 缩放比
    time = db.Column(db.String)  # 添加时间

    def __repr__(self):
        return "<Spotinf %r>" % self.id


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    articleid = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    userid = db.Column(db.Integer)


class Spotsite(db.Model):
    __tablename__ = 'spotsite'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    uuid = db.Column(db.String)
    money = db.Column(db.Float)
    face = db.Column(db.String)

    def __repr__(self):
        return "<Comment %r>" % self.id

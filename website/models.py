from . import db
from flask_login import UserMixin
import datetime as dt


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class MyDateTime(db.TypeDecorator):
    impl = db.DateTime
    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return dt.datetime.strptime(value, '%d-%b-%y %H:%M:%S')
        return value

class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    profile_pic = db.Column(db.String(20), default='/static/profile_pic/spt.jpg')
    date_created = db.Column(MyDateTime, default=((dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime('%d-%b-%y %H:%M:%S')))
    posts = db.relationship('post', backref='author')
    followed = db.relationship(
        'user', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, User):
        if not self.is_following(User):
            self.followed.append(User)

    def unfollow(self, User):
        if self.is_following(User):
            self.followed.remove(User)

    def is_following(self, User):
        return self.followed.filter(
            followers.c.followed_id == User.id).count() > 0
    
    def followed_post(self):
        followed = post.query.join(
            followers, (followers.c.followed_id == post.author_user)).filter(
                followers.c.follower_id == self.id)
        own = post.query.filter_by(author_user=self.id)
        return followed.union(own).order_by(post.date_created.desc())

class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    caption = db.Column(db.Text(150))
    image = db.Column(db.String(20))
    author_user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(MyDateTime, default=((dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).strftime('%d-%b-%y %H:%M:%S')))

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed

class ImageUpload(FlaskForm):
    picture = FileField('Edit Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

class PostUpload(FlaskForm):
    picture = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])


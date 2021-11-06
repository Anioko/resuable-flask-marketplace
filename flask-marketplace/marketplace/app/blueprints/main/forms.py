from app.models import *
from flask_ckeditor import CKEditorField
from flask_uploads import UploadSet, IMAGES
from flask_wtf import Form, FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import IntegerField, StringField, SubmitField, DateField, TextAreaField, FormField, MultipleFileField, \
    RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Required, ValidationError, InputRequired, Email

images = UploadSet('images', IMAGES)
docs = UploadSet('docs', ('rtf', 'odf', 'ods', 'gnumeric', 'abw', 'doc', 'docx', 'xls', 'xlsx', 'pdf'))


class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code', validators=[Required()])
    area_code = IntegerField('Area Code/Exchange', validators=[Required()])
    number = StringField('Number')


class ContactForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)


class PhotoForm(FlaskForm):
    photo = FileField('Image file', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    submit = SubmitField('Submit')


class TagForm(FlaskForm):
    tag = StringField('Please tag your question', validators=[DataRequired()])



class AnswerForm(FlaskForm):
    """ This is the question answers form  """
    body = TextAreaField('Answers', validators=[DataRequired(), Length(min=2, max=5000)])
    submit = SubmitField('Answer')


class MessageForm(FlaskForm):
    message = StringField(('Message'), validators=[
        DataRequired(), Length(min=1, max=2500)])
    submit = SubmitField(('Submit'))


# class MessageForm(FlaskForm):
#     """ This is the messageform  """
#     body = TextAreaField('Message', validators=[Required(), Length(min=50, max=5000)])
#     submit = SubmitField('Submit')
#
# class ReplyForm(FlaskForm):
#     """ This is the message reply form  """
#     body = TextAreaField('Reply', validators=[Required(), Length(min=50, max=5000)])
#     submit = SubmitField('Submit')


class PostForm(FlaskForm):
    # image = FileField('Image', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    text = TextAreaField('')
    photo = MultipleFileField('Add Photos', validators=[FileAllowed(images, 'Images only!')])
    post_privacy = RadioField('Privacy', choices=[('0', 'Everyone'), ('1', 'Followers Only'), ('2', 'Private')],
                              default='0')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    """ This is the comments form  """
    body = TextAreaField('Comments', validators=[DataRequired(), Length(min=50, max=5000)])
    submit = SubmitField('Submit')


class InviteUserForm(FlaskForm):
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

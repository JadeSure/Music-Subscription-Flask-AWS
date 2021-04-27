from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class QueryForm(FlaskForm):
    title = StringField(label = 'Title: ')
    year = StringField(label = 'Year: ')
    artist = StringField(label='Artist: ')

    query = SubmitField(label = 'Submit')
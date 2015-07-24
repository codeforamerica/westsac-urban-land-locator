from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField, DecimalField, IntegerField
from wtforms.validators import DataRequired

from farmsList.user.models import User

class LoginForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append('Unknown username')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        if not self.user.active:
            self.username.errors.append('User not activated')
            return False
        return True

class ContactLandOwnerForm(Form):
    name = TextField('Name', validators=[DataRequired()])
    email = TextField('Email', validators=[DataRequired()])
    phone = TextField('Phone')
    website = TextField('Website')
    cropPlan = TextField('What do you plan to farm on the property?', validators=[DataRequired()])
    otherBackground = TextField('Do you own any other farms? If so, where?', validators=[DataRequired()])
    additionalInfo = TextField('Anything else?')

    def __init__(self, *args, **kwargs):
        super(ContactLandOwnerForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(ContactLandOwnerForm, self).validate()
        if not initial_validation:
            return False
        return True

class NewParcel1Form(Form):
    address = TextField('Address', validators=[DataRequired()])
    water = TextField('Water', validators=[DataRequired()])
    soil = TextField('Soil')
    size = DecimalField('Size (in acres)', validators=[DataRequired()])
    zoning = TextField('Zoning', validators=[DataRequired()])
    developmentPlan = TextField('Maximum Lease', validators=[DataRequired()])
    restrictions = TextField('Use Restrictions', validators=[DataRequired()])
    email = TextField('Contact e-mail', validators=[DataRequired()])
    geometry = TextField('Geometry', validators=[DataRequired()])
    center = TextField('Center', validators=[DataRequired()])
    apn = IntegerField('APN', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(NewParcel1Form, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(NewParcel1Form, self).validate()
        if not initial_validation:
            return False
        return True

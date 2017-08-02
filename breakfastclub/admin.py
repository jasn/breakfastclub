from breakfastclub import app, db, login_manager, models

from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

class BreakfastclubModelView(ModelView):

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return login_manager.unauthorized()

class BreakfastclubAdminIndexView(AdminIndexView):

    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_admin:
            return login_manager.unauthorized()
        return super().index()

admin = Admin(app, name='breakfastclub', index_view=BreakfastclubAdminIndexView())

admin.add_view(BreakfastclubModelView(models.Person, db.session))
admin.add_view(BreakfastclubModelView(models.BreadList, db.session))


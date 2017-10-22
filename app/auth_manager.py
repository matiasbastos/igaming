from flask import flash, g, redirect
from flask_appbuilder import expose
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.forms import LoginForm_db
from flask_appbuilder.security.views import AuthView
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_login import login_user
from igamming_platform import Game


class CustomAuthDBView(AuthView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_db(form.username.data,
                                                   form.password.data)
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)
            # Game Event: on_login
            game = Game(str(user.id))
            game.on_event('on_login')
            return redirect(self.appbuilder.get_url_for_index)
        return self.render_template(self.login_template,
                               title=self.title,
                               form=form,
                               appbuilder=self.appbuilder)


class CustomSecurityManager(SecurityManager):
    authdbview = CustomAuthDBView

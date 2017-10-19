from flask import g
from flask_appbuilder import BaseView, expose


class Index(BaseView):
    """
        A simple view that implements the index for the site
    """
    route_base = ''
    default_view = 'index'
    index_template = 'index.html'

    @expose('/')
    def index(self):
        if g.user.is_authenticated():
            self.index_template = 'game_index.html'
        else:
            self.index_template = 'index.html'

        self.update_redirect()
        return self.render_template(self.index_template,
                                    appbuilder=self.appbuilder)

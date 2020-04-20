from rest_framework.routers import APIRootView, DefaultRouter


class ScorpioAPIRootView(APIRootView):
    """Root of the Scorpio API. This router adds additional routes to the API Root."""
    name = "Scorpio API"

    def get(self, request, *args, **kwargs):
        self.api_root_dict.update([('index/add', 'index-add'),
                                   ('index/delete', 'index-delete'),
                                   ('index/reset', 'index-reset'),
                                   ('schema', 'schema')])
        return super(ScorpioAPIRootView, self).get(request, *args, **kwargs)


class ScorpioRouter(DefaultRouter):
    APIRootView = ScorpioAPIRootView

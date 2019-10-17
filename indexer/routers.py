from rest_framework.routers import DefaultRouter, APIRootView, Route


class ScorpioAPIRootView(APIRootView):
    """Root of the Rockefeller Archive Center API"""
    name = "Scorpio API"

    def get(self, request, *args, **kwargs):
        # Add endpoints to API Root
        self.api_root_dict.update([('index/add', 'index-add'),
                                   ('index/delete', 'index-delete'),
                                   ('merge', 'merge'),
                                   ('schema', 'schema')])
        return super(ScorpioAPIRootView, self).get(request, *args, **kwargs)


class ScorpioRouter(DefaultRouter):
    APIRootView = ScorpioAPIRootView

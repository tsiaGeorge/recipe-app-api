from rest_framework import routers
from . import views

app_name = 'recipe'

router = routers.DefaultRouter()
router.register(r'tag', views.TagViewSet)
urlpatterns = router.urls

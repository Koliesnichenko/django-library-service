from rest_framework import routers

from borrowings.views import BorrowingViewSet

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet, basename="borrowing")

urlpatterns = router.urls

app_name = "borrowings"

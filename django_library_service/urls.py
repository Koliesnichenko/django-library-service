"""
URL configuration for django_library_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin

from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django_library_service import settings
from payments.views import PaymentCancelView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/payments/", include("payments.urls", namespace="payments")),
    path("api/books/", include("books.urls", namespace="books")),
    path("api/user/", include("user.urls", namespace="users")),
    path("api/borrowings/", include("borrowings.urls", namespace="borrowings")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

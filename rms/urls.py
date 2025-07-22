"""
URL configuration for rms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name="dashboard"),

    # Category URLs
    path('add-category/', add_category, name="add_category"),
    path('view-category/', view_category, name="view_category"),
    path('edit-category/<int:pid>/', edit_category, name="edit_category"),
    path('delete-category/<int:pid>/', delete_category, name="delete_category"),
    # Product URLs
    path('add-product/', add_product, name="add_product"),
    path('view-product/', view_product, name="view_product"),
    path('edit-product/<int:pid>/', edit_product, name="edit_product"),
    path('delete-product/<int:pid>/', delete_product, name="delete_product"),
    # POS URLs
    path('pos/', pos, name="pos"),
    path('clear-cart/', clear_cart, name="clear_cart"),

    path('checkout/', checkout_view, name="checkout"),

    path('receipt/<int:sale_id>/', show_receipt, name='receipt'),  # optional view to show receipt by ID

    # Expense URLs
    path('add-expense/', add_expense, name="add_expense"),
    path('view-expenses/', view_expenses, name='view_expenses'),
    path('edit-expense/<int:id>/', edit_expense, name='edit_expense'),
    path('delete-expense/<int:pid>/', delete_expense, name='delete_expense'),


    

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


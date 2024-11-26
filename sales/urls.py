from unicodedata import name
from django.urls import path
from django.views.generic import TemplateView
from .views import *
from .sparrow import *
from utility.mailjet import *
app_name = 'sales'

urlpatterns = [

path('order/list/',OrderList.as_view(),name='order-list'),
path('order/create/',OrderCreate.as_view(),name='create-order'),
path('custom-order/create/',CustomOrderCreate.as_view(),name='custom-create-order'),
path('order/view/<int:id>/',ViewOrder.as_view(), name='view-order'),
path('order/edit/<int:id>/',OrderUpdate.as_view(), name='order-update'),
path('order/invoice/<int:id>/',OrderInvoice.as_view(), name='invoice-order'),
path('order/delete/<int:pk>/',deleteOrder,name='delete-order'),
path('order/item/delete/<int:pk>/',deleteOrderItem,name='order-item-delete'),
path('order/bulk/delete/',deleteOrderBulk,name='order-bulk-delete'),
path('custom-order-update/<int:pk>/',CustomOrderUpdate.as_view(),name = 'custom-order-update'),
path('order/item/update',orderItemUpdate,name='order-item-update'),
path('order/item/create',orderItemCreate,name='order-item-create'),
path('ajax/order-status/update', orderStatusUpdate, name='order-status-update'),
path('ajax/payment-status/update',paymentStatusUpdate, name='payment-status-update'),
path('order-item-update-quantity',update_order_item_quantity, name='order-quantity-update'),
path('ajax/order-delivery-status/update/',deliveryStatusUpdate, name='order-delivery-status-update'),
path('assigned/delivery/bulk-delete/',deliveryAssignBulkDelete,name='delivery-assigned-bulk-delete'),
path('assigned/delivery/delete/<int:pk>/',deleteOrderAssigned,name='delete-delivery-assigned'),
path('update-price-of-custom-order/',customOrderPriceUpdate,name = 'update-price-of-custom-order'),
path('update-flavour-of-custom-order/',customOrderFlavourUpdate,name = 'update-flavour-of-custom-order'),
path('update-pound-of-custom-order/',customOrderPoundUpdate,name = 'update-pound-of-custom-order'),
path('send-email-order-status/',send_email_order_status,name='send-email-order-status'),
path('delivery/board/<str:day>/',DeliveryBoard.as_view(),name='delivery-board'),
path('ajax/assign-delivery-boy/',assignDeliveryBoy, name='ajax-assign-delivery-boy'),
path('order/assigned-to/',orderAssignedToDeliveryBoy,name='order-assign-to-delivery-boy'),
path('check-order-status/',checkOrderStatus,name='check-order-status'),
path('update/order-status/',updateOrderStatus,name='order-status-update-deliveryboard'),
path('get/order-item/detail',orderDetail,name='get-item-detail'),
path('latest/order/',latestOrder,name='latest-order'),


path('orders-cancelled/', canceledOrders, name='cancelled-order-list'),

path('ajax/get-varient-list/',getVarientList,name='get-product-varient'),
path('ajax/get-varient/',getVarient,name='get-varient'),
path('ajax/get-addons/',getAddons,name='get-addons'),
path('ajax/get-time/',getTime,name='get-time'), 
path('sales_over_time/', SalesOverTimeView.as_view(),name="sales-over-time"),
path('export_sales_over_time_csv/', ExportCsvViewSalesOverTime.as_view(), name="export-sells-over-time-csv"),
path('sales_by_product/', SalseByProductView.as_view(), name="sales-by-product"), 
path('export_csv_product/', ExportSalesByProductView.as_view(), name="export-csv-product"),
path('sales_by_costumer/', SalesByCostumer.as_view(), name='sales-by-costumer'),
path('export_csv_costumer', SalesByCostumerExportCSView.as_view(), name='export-csv-costumer'),
path('order_report', OrderReport.as_view(), name="order-report"),
path('export_csv_order_report', ExportOrderReportToCsv.as_view(), name="export-csv-order-report"),
path('ajax/get-time/',getTime,name='get-time'),


path('vendor/',vendorList,name="vendor-list"),
path('vendor/delete/<int:pk>/',vendorDelete,name="vendor-delete"),
path('ajax/vendor/create/',vendorAjaxCreate,name="ajax-vendor-create"),
path('ajax/vendor/update/<int:pk>/',vendorAjaxUpdate,name="ajax-vendor-update"),
path('vendor/bulk/delete/',deleteVendorBulk,name='vendor-bulk-delete'),

path('factory/',factoryList,name="factory-list"),
path('factory/delete/<int:pk>/',factoryDelete,name="factory-delete"),
path('ajax/factory/create/',factoryAjaxCreate,name="ajax-factory-create"),
path('ajax/factory/update/<int:pk>/',factoryAjaxUpdate,name="ajax-factory-update"),
path('factory/bulk/delete/',deleteFactoryBulk,name='factory-bulk-delete'),

path('export/order/xls/', export_order_xls, name='export_order_xls'),
path('export/sales/xls/', export_sales_xls, name='export_sales_xls'),

path('order-detail-to-customer/<str:order_number>/',OrderToCustomer.as_view(), name='order-detail-to-customer'),


path('order-alert/',orderAlertList,name="order-alert-list"),
path('order-alert/delete/<int:pk>/',orderAlertDelete,name="order-alert-delete"),
path('ajax/order-alert/create/',orderAlertAjaxCreate,name="ajax-order-alert-create"),
path('ajax/order-alert/update/<int:pk>/',orderAlertAjaxUpdate,name="ajax-order-alert-update"),
path('order-alert/bulk/delete/',deleteOrderAlertBulk,name='order-alert-bulk-delete'),



path('export-order-log/', export_order_logs_to_csv, name = 'export-order-log'),
path('all_odo/', all_order_push_odo, name="all_order_push_odo"),
path('all_failed/', push_all_failed_order_to_odoo, name="all_failed"),
path('push_odoo/', push_order_list_odoo,name="push-odoo")
]

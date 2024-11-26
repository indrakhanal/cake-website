from rest_framework import permissions
from users.models import Users
from django.shortcuts import get_object_or_404

class IsVendor(permissions.BasePermission):
	message = 'Permission Denied'
	def has_permission(self, request, view):
		if request.user.profile.is_vendor:
			return True
		return False

class IsDispatcher(permissions.BasePermission):
	message = 'Permission Denied'
	def has_permission(self, request, view):
		if request.user.profile.is_dispatcher:
			return True
		return False

class IsDeliveryBoy(permissions.BasePermission):
	message = 'Permission Denied'
	def has_permission(self, request, view):
		if request.user.profile.is_delivery_person:
			return True
		return False
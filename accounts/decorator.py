from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group

class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def __init__(self):
        super().__init__()
        self.request = None

    def test_func(self):
      groups=Group.objects.all()
      if self.request.user.is_superuser:
        return True
      for i in self.request.user.groups.all():
        if i in groups:
          return True
      return False


from functools import wraps
from django.http import HttpResponseRedirect

def groupRequired(function=None):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    print('----')
    groups=Group.objects.all()
    if self.request.user.is_superuser:
      return wrap
    for i in self.request.user.groups.all():
      if i in groups:
        print(i.perms)
        return wrap
    return HttpResponseRedirect('/')
     
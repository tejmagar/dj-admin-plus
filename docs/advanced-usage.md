# DJ Admin plus

## Permission
By default, the admin interface is login and permission protected.
It means, the user with permission only can perform operation for model navigation.

However, you can implement your custom permission check manually.

```python
from dj_admin_plus.navigation import Navigation


def can_access_dashboard(request):
    return False  # Return a boolean value


...

Navigation(
    _id='dashboard',
    title='Dashboard',
    icon_class='fa-gauge-high',
    permission_check=can_access_dashboard  # Add your custom permission check here
)
...
```

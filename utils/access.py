def is_admin(user):
    return user and user.role in ("admin", "super-admin")

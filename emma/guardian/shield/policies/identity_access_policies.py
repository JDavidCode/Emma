class Identity:
    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role


class AccessPolicy:
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

    def grant_permission(self, permission):
        self.permissions.append(permission)

    def revoke_permission(self, permission):
        self.permissions.remove(permission)

    def check_permission(self, permission):
        return permission in self.permissions

    def get_permissions(self):
        return self.permissions

    def update_permissions(self, new_permissions):
        self.permissions = new_permissions

    def merge_policy(self, other_policy):
        merged_permissions = list(set(self.permissions + other_policy.get_permissions()))
        self.update_permissions(merged_permissions)

from .common import BaseTransactionCase

# (model, viewer RWCD, user RWCD, manager RWCD) - mirrors security/ir.model.access.csv,
# which mirrors the README's Access-per-model table.
ACCESS_MATRIX = [
    ("im.product.category", "r---", "r---", "rwcd"),
    ("im.product", "r---", "r---", "rwcd"),
    ("res.partner", "r---", "r---", "rwc-"),
    ("im.warehouse", "r---", "r---", "rwcd"),
    ("im.location", "r---", "r---", "rwcd"),
    ("im.purchase.order", "r---", "rwc-", "rwcd"),
    ("im.purchase.line", "r---", "rwc-", "rwcd"),
    ("im.sale.order", "r---", "rwc-", "rwcd"),
    ("im.sale.line", "r---", "rwc-", "rwcd"),
    ("im.shipment", "r---", "rwc-", "rwcd"),
    ("im.move", "r---", "rwc-", "rwcd"),
    ("im.quant", "r---", "r---", "r---"),
    ("im.adjustment", "----", "r---", "rwc-"),
    ("im.alert", "r---", "rw--", "rwcd"),
]

OPERATIONS = [("r", "read"), ("w", "write"), ("c", "create"), ("d", "unlink")]


class TestAccessMatrix(BaseTransactionCase):
    def setUp(self):
        super().setUp()
        self.role_users = {
            role: self._create_role_user(f"Matrix {role.capitalize()}", f"matrix.{role}@example.com", role)
            for role in ("viewer", "user", "manager")
        }

    def test_access_matrix_matches_readme_table(self):
        failures = []
        for model, viewer_perms, user_perms, manager_perms in ACCESS_MATRIX:
            expected_by_role = {
                "viewer": viewer_perms,
                "user": user_perms,
                "manager": manager_perms,
            }
            for role, expected in expected_by_role.items():
                user = self.role_users[role]
                scoped_model = self.env[model].with_user(user).browse()
                for letter, operation in OPERATIONS:
                    expected_allowed = letter in expected
                    actual_allowed = scoped_model.has_access(operation)
                    if actual_allowed != expected_allowed:
                        failures.append(
                            f"{model}: {role} {operation} expected "
                            f"{'allowed' if expected_allowed else 'denied'}, "
                            f"got {'allowed' if actual_allowed else 'denied'}"
                        )
        self.assertFalse(failures, "\n".join(failures))

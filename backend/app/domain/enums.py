"""Domain sabitleri. Hiçbir framework'e bağımlı değildir."""
from enum import Enum


class Role(str, Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"      # İade edilmemiş, süresi geçmemiş
    OVERDUE = "OVERDUE"    # İade edilmemiş, son iade tarihi geçmiş
    RETURNED = "RETURNED"  # İade edilmiş


class DeleteAction(str, Enum):
    DELETED = "DELETED"
    DEACTIVATED = "DEACTIVATED"

"""Kategori yönetimi iş akışları."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import transaction
from app.domain.enums import DeleteAction
from app.domain.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.book import DeleteResult
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

DUPLICATE_NAME = "Bu isimde bir kategori zaten var."


class CategoryService:
    def __init__(self, session: Session):
        self.session = session
        self.categories = CategoryRepository(session)

    def _to_out(self, category: Category) -> CategoryOut:
        out = CategoryOut.model_validate(category)
        out.book_count = self.categories.count_books(category.id)
        return out

    def list_categories(self, *, include_inactive: bool) -> list[CategoryOut]:
        result = []
        for category, count in self.categories.list_with_counts(include_inactive=include_inactive):
            out = CategoryOut.model_validate(category)
            out.book_count = count
            result.append(out)
        return result

    def create(self, data: CategoryCreate) -> CategoryOut:
        if self.categories.get_by_name(data.name):
            raise ConflictError(DUPLICATE_NAME, "KATEGORI_ADI_KULLANIMDA")
        category = Category(name=data.name, description=data.description or None, is_active=True)
        try:
            with transaction(self.session):
                self.categories.add(category)
                self.session.flush()
        except IntegrityError as exc:
            raise ConflictError(DUPLICATE_NAME, "KATEGORI_ADI_KULLANIMDA") from exc
        return self._to_out(category)

    def update(self, category_id: int, data: CategoryUpdate) -> CategoryOut:
        category = self.categories.get(category_id)
        if category is None:
            raise NotFoundError("Kategori bulunamadı.")
        changes = data.model_dump(exclude_unset=True)
        if "name" in changes:
            if changes["name"] is None:
                raise BusinessRuleError("Kategori adı boş bırakılamaz.", "ZORUNLU_ALAN")
            existing = self.categories.get_by_name(changes["name"])
            if existing and existing.id != category.id:
                raise ConflictError(DUPLICATE_NAME, "KATEGORI_ADI_KULLANIMDA")
        if "is_active" in changes and changes["is_active"] is None:
            raise BusinessRuleError("Aktiflik durumu boş bırakılamaz.", "ZORUNLU_ALAN")
        try:
            with transaction(self.session):
                for field, value in changes.items():
                    setattr(category, field, value if value != "" else None)
        except IntegrityError as exc:
            raise ConflictError(DUPLICATE_NAME, "KATEGORI_ADI_KULLANIMDA") from exc
        return self._to_out(category)

    def delete(self, category_id: int) -> DeleteResult:
        """Kitabı olan kategori fiziksel olarak silinmez, pasifleştirilir."""
        category = self.categories.get(category_id)
        if category is None:
            raise NotFoundError("Kategori bulunamadı.")
        with transaction(self.session):
            if self.categories.count_books(category.id) > 0:
                category.is_active = False
                return_value = DeleteResult(
                    id=category_id,
                    action=DeleteAction.DEACTIVATED,
                    message="Kategoriye bağlı kitaplar olduğu için kategori silinmedi, pasifleştirildi.",
                )
            else:
                self.categories.delete(category)
                return_value = DeleteResult(
                    id=category_id, action=DeleteAction.DELETED, message="Kategori silindi."
                )
        return return_value

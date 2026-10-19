"""İlk veritabanı şeması: users, categories, books, loans, revoked_tokens

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-18 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. USERS tablosu
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_number', sa.String(length=20), nullable=True),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='STUDENT', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('must_change_password', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('STUDENT', 'ADMIN')", name='ck_users_role_valid'),
        sa.CheckConstraint("role = 'ADMIN' OR student_number IS NOT NULL", name='ck_users_student_has_number'),
        sa.CheckConstraint('failed_login_attempts >= 0', name='ck_users_failed_logins_non_negative'),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('student_number', name='uq_users_student_number')
    )

    # 2. CATEGORIES tablosu
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('length(trim(name)) >= 2', name='ck_categories_name_min_length'),
        sa.PrimaryKeyConstraint('id', name='pk_categories')
    )
    op.create_index('uq_categories_name_lower', 'categories', [sa.text('lower(name)')], unique=True)

    # 3. BOOKS tablosu
    op.create_table(
        'books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('isbn', sa.String(length=13), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('author', sa.String(length=160), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('publisher', sa.String(length=160), nullable=True),
        sa.Column('publication_year', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('shelf_location', sa.String(length=40), nullable=True),
        sa.Column('total_copies', sa.Integer(), server_default='0', nullable=False),
        sa.Column('available_copies', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('total_copies >= 0', name='ck_books_total_copies_non_negative'),
        sa.CheckConstraint('available_copies >= 0', name='ck_books_available_copies_non_negative'),
        sa.CheckConstraint('available_copies <= total_copies', name='ck_books_available_not_exceed_total'),
        sa.CheckConstraint('publication_year IS NULL OR publication_year BETWEEN 1450 AND 2100', name='ck_books_publication_year_range'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_books_category_id_categories', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_books'),
        sa.UniqueConstraint('isbn', name='uq_books_isbn')
    )
    op.create_index('ix_books_title', 'books', ['title'])
    op.create_index('ix_books_author', 'books', ['author'])
    op.create_index('ix_books_category_id', 'books', ['category_id'])
    op.create_index('ix_books_is_active', 'books', ['is_active'])

    # 4. LOANS tablosu
    op.create_table(
        'loans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('borrowed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('returned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('due_at > borrowed_at', name='ck_loans_due_after_borrow'),
        sa.CheckConstraint('returned_at IS NULL OR returned_at >= borrowed_at', name='ck_loans_return_after_borrow'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], name='fk_loans_book_id_books', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_loans_user_id_users', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name='pk_loans')
    )
    op.create_index('ix_loans_user_id', 'loans', ['user_id'])
    op.create_index('ix_loans_book_id', 'loans', ['book_id'])
    op.create_index('ix_loans_borrowed_at', 'loans', ['borrowed_at'])
    # Kural 5: Aynı öğrenci aynı kitap için yalnızca bir aktif ödünç kaydına sahip olabilir
    op.create_index(
        'uq_loans_active_user_book',
        'loans',
        ['user_id', 'book_id'],
        unique=True,
        postgresql_where=sa.text('returned_at IS NULL')
    )
    op.create_index(
        'ix_loans_active_due_at',
        'loans',
        ['due_at'],
        postgresql_where=sa.text('returned_at IS NULL')
    )

    # 5. REVOKED_TOKENS tablosu
    op.create_table(
        'revoked_tokens',
        sa.Column('jti', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('jti', name='pk_revoked_tokens')
    )
    op.create_index('ix_revoked_tokens_expires_at', 'revoked_tokens', ['expires_at'])


def downgrade() -> None:
    op.drop_table('revoked_tokens')
    op.drop_table('loans')
    op.drop_table('books')
    op.drop_table('categories')
    op.drop_table('users')

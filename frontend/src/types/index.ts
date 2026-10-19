export type Role = 'STUDENT' | 'ADMIN';

export type LoanStatus = 'ACTIVE' | 'OVERDUE' | 'RETURNED';

export type DeleteAction = 'DELETED' | 'DEACTIVATED';

export interface User {
  id: number;
  student_number: string | null;
  full_name: string;
  email: string;
  role: Role;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
}

export interface UserSummary {
  id: number;
  student_number: string | null;
  full_name: string;
  email: string;
}

export interface CategorySummary {
  id: number;
  name: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  book_count: number;
}

export interface Book {
  id: number;
  isbn: string;
  title: string;
  author: string;
  description: string | null;
  publisher: string | null;
  publication_year: number | null;
  category_id: number | null;
  category: CategorySummary | null;
  shelf_location: string | null;
  total_copies: number;
  available_copies: number;
  is_active: boolean;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookSummary {
  id: number;
  isbn: string;
  title: string;
  author: string;
}

export interface Loan {
  id: number;
  user: UserSummary;
  book: BookSummary;
  borrowed_at: string;
  due_at: string;
  returned_at: string | null;
  status: LoanStatus;
  is_overdue: boolean;
  overdue_days: number;
  late_return_days: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ActivityItem {
  loan_id: number;
  type: 'BORROW' | 'RETURN';
  occurred_at: string;
  student_number: string | null;
  full_name: string;
  book_title: string;
}

export interface DashboardStats {
  active_book_titles: number;
  total_copies: number;
  available_copies: number;
  active_loans: number;
  overdue_loans: number;
  active_students: number;
  total_categories: number;
  recent_activity: ActivityItem[];
  generated_at: string;
}

export interface OverdueItem {
  loan_id: number;
  user_id: number;
  student_number: string | null;
  full_name: string;
  email: string;
  book_id: number;
  book_title: string;
  isbn: string;
  borrowed_at: string;
  due_at: string;
  overdue_days: number;
}

export interface OverdueReport {
  items: OverdueItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  generated_at: string;
  start_date: string | null;
  end_date: string | null;
}

export interface ErrorDetail {
  field?: string | null;
  message: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: ErrorDetail[];
}

export interface DeleteResult {
  id: number;
  action: DeleteAction;
  message: string;
}

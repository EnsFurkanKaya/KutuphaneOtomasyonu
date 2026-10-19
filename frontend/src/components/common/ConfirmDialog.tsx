import React, { ReactNode } from 'react';
import { AlertCircle, HelpCircle, CheckCircle2 } from 'lucide-react';

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string | ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'primary' | 'danger' | 'warning';
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Onayla',
  cancelLabel = 'Vazgeç',
  variant = 'primary',
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  const variantStyles = {
    primary: {
      icon: <HelpCircle className="w-6 h-6 text-brand-600" />,
      bg: 'bg-brand-50',
      button: 'bg-brand-600 hover:bg-brand-700 text-white',
    },
    warning: {
      icon: <AlertCircle className="w-6 h-6 text-amber-600" />,
      bg: 'bg-amber-50',
      button: 'bg-amber-600 hover:bg-amber-700 text-white',
    },
    danger: {
      icon: <AlertCircle className="w-6 h-6 text-rose-600" />,
      bg: 'bg-rose-50',
      button: 'bg-rose-600 hover:bg-rose-700 text-white',
    },
  }[variant];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-150">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl shrink-0 ${variantStyles.bg}`}>
              {variantStyles.icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-slate-900 mb-2">{title}</h3>
              <div className="text-sm text-slate-600 leading-relaxed">{message}</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-50 px-6 py-4 flex items-center justify-end gap-3 border-t border-slate-100">
          <button
            type="button"
            disabled={isLoading}
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200/60 rounded-xl transition-colors disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            disabled={isLoading}
            onClick={onConfirm}
            className={`px-5 py-2 text-sm font-semibold rounded-xl shadow-sm transition-all disabled:opacity-50 flex items-center gap-2 ${variantStyles.button}`}
          >
            {isLoading ? (
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

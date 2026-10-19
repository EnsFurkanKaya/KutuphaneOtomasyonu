import React from 'react';
import { getLoanStatusInfo, getBookAvailabilityInfo } from '../../utils/formatters';

interface LoanStatusBadgeProps {
  status: string;
}

export const LoanStatusBadge: React.FC<LoanStatusBadgeProps> = ({ status }) => {
  const info = getLoanStatusInfo(status);
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${info.colorClass}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${info.dotClass}`} />
      {info.label}
    </span>
  );
};

interface BookAvailabilityBadgeProps {
  isAvailable: boolean;
  copies: number;
}

export const BookAvailabilityBadge: React.FC<BookAvailabilityBadgeProps> = ({
  isAvailable,
  copies,
}) => {
  const info = getBookAvailabilityInfo(isAvailable, copies);
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${info.colorClass}`}
    >
      {info.label}
    </span>
  );
};

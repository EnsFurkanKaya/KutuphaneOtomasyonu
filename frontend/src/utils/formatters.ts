/**
 * Tarih ve veri biçimlendirme yardımcıları.
 * Tarihler Türkçe standartlarına uygun (dd.MM.yyyy) biçimlendirilir.
 */

export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) return '-';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '-';
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}.${month}.${year}`;
  } catch {
    return '-';
  }
}

export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return '-';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '-';
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${day}.${month}.${year} ${hours}:${minutes}`;
  } catch {
    return '-';
  }
}

export function getLoanStatusInfo(status: string) {
  switch (status) {
    case 'ACTIVE':
      return {
        label: 'Aktif Ödünç',
        colorClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        dotClass: 'bg-emerald-500',
      };
    case 'OVERDUE':
      return {
        label: 'Gecikmiş',
        colorClass: 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse',
        dotClass: 'bg-rose-500',
      };
    case 'RETURNED':
      return {
        label: 'İade Edildi',
        colorClass: 'bg-slate-100 text-slate-700 border-slate-200',
        dotClass: 'bg-slate-400',
      };
    default:
      return {
        label: status,
        colorClass: 'bg-slate-100 text-slate-600 border-slate-200',
        dotClass: 'bg-slate-400',
      };
  }
}

export function getBookAvailabilityInfo(isAvailable: boolean, copies: number) {
  if (copies <= 0 || !isAvailable) {
    return {
      label: 'Mevcut Değil (0 Stok)',
      colorClass: 'bg-amber-50 text-amber-700 border-amber-200',
      badgeClass: 'bg-amber-100 text-amber-800',
    };
  }
  return {
    label: `${copies} Adet Uygun`,
    colorClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    badgeClass: 'bg-emerald-100 text-emerald-800',
  };
}

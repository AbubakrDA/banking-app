import React, { TableHTMLAttributes, HTMLAttributes } from 'react';

export const Table: React.FC<TableHTMLAttributes<HTMLTableElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className="w-full overflow-x-auto rounded-card border border-border-subtle">
    <table className={`w-full text-left text-xs ${className}`} {...props}>
      {children}
    </table>
  </div>
);

export const TableHeader: React.FC<HTMLAttributes<HTMLTableSectionElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <thead className={`bg-surface-subdued text-navy font-semibold border-b border-border-subtle ${className}`} {...props}>
    {children}
  </thead>
);

export const TableBody: React.FC<HTMLAttributes<HTMLTableSectionElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <tbody className={`divide-y divide-border-subtle bg-surface ${className}`} {...props}>
    {children}
  </tbody>
);

export const TableRow: React.FC<HTMLAttributes<HTMLTableRowElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <tr className={`hover:bg-surface-hover transition-colors ${className}`} {...props}>
    {children}
  </tr>
);

export const TableHead: React.FC<HTMLAttributes<HTMLTableCellElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <th className={`px-4 py-3 text-navy-secondary font-semibold uppercase tracking-wider text-[11px] ${className}`} {...props}>
    {children}
  </th>
);

export const TableCell: React.FC<HTMLAttributes<HTMLTableCellElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <td className={`px-4 py-3 text-navy ${className}`} {...props}>
    {children}
  </td>
);

export default Table;

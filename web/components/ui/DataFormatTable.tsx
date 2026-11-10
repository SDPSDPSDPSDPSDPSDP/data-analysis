import type { DataFormat } from "@/lib/sections";

const NUMERIC_CELL = /^[-+]?[\d.,]*\d%?$/;

export default function DataFormatTable({ columns, rows }: Pick<DataFormat, "columns" | "rows">) {
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.name}>
                {col.name} <span className="data-table-role">{col.role}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} className={NUMERIC_CELL.test(cell) ? "data-table-num" : undefined}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

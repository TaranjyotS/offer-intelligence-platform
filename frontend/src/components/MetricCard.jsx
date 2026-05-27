export default function MetricCard({ label, value, hint }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
      {hint ? <span>{hint}</span> : null}
    </div>
  );
}

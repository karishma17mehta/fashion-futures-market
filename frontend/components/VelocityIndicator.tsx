/**
 * VelocityIndicator — shows signal_velocity as a directional arrow + value.
 * Green up arrow for rising, red down for fading, neutral for flat.
 */
export default function VelocityIndicator({ velocity }: { velocity: number }) {
  const isRising = velocity > 5;
  const isFading = velocity < -5;
  const abs = Math.abs(velocity);

  const color = isRising ? "#6abf87" : isFading ? "#e86060" : "rgba(245,240,235,0.3)";
  const arrow = isRising ? "↑" : isFading ? "↓" : "→";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "3px",
        fontSize: "10px",
        color,
        fontFamily: "Inter, sans-serif",
        fontWeight: 400,
      }}
    >
      <span style={{ fontSize: "11px" }}>{arrow}</span>
      <span>{abs.toFixed(1)}%</span>
    </span>
  );
}

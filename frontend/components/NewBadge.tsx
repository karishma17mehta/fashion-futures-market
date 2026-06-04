/**
 * NewBadge - shows a pulsing "NEW" indicator for trends detected in the last 48h.
 */
export default function NewBadge({ createdAt }: { createdAt: string }) {
  const ageMs = Date.now() - new Date(createdAt).getTime();
  const ageHours = ageMs / (1000 * 60 * 60);
  if (ageHours > 48) return null;

  const label = ageHours < 1
    ? "Just now"
    : ageHours < 24
    ? `${Math.floor(ageHours)}h ago`
    : "New";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: "2px 8px",
        fontSize: "9px",
        letterSpacing: "0.15em",
        textTransform: "uppercase",
        color: "#6abf87",
        background: "rgba(106,191,135,0.1)",
        border: "1px solid rgba(106,191,135,0.25)",
        borderRadius: "2px",
      }}
    >
      <span
        style={{
          display: "inline-block",
          width: "5px",
          height: "5px",
          borderRadius: "50%",
          background: "#6abf87",
          animation: "pulse 2s infinite",
        }}
      />
      {label}
    </span>
  );
}

export default function ErrorBar({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="error-bar">
      <span>{message}</span>
      <button onClick={onDismiss} aria-label="Dismiss">
        ×
      </button>
    </div>
  );
}

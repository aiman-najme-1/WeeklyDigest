export default function LoadingState({ title, description }) {
  return (
    <section className="loading-state" role="status" aria-live="polite">
      <div className="loader" aria-hidden="true" />
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </section>
  );
}

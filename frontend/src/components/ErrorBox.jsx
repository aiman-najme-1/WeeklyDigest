export default function ErrorBox({ kicker, title, message }) {
  if (!message) {
    return null;
  }

  return (
    <section className="error-box" role="alert">
      <p className="section-kicker">{kicker}</p>
      <h2>{title}</h2>
      {message !== title && <p>{message}</p>}
    </section>
  );
}

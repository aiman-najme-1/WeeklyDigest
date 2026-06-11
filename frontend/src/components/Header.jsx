export default function Header({ content }) {
  return (
    <header className="hero">
      <div className="hero__content">
        <p className="hero__eyebrow">{content.eyebrow}</p>
        <h1>WeeklyDigest</h1>
        <p className="hero__subtitle">{content.subtitle}</p>
        <p className="hero__description">{content.description}</p>
      </div>

      <div className="hero__stats" aria-label={content.statsLabel}>
        {content.stats.map(([value, label]) => (
          <div key={`${value}-${label}`}>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </header>
  );
}

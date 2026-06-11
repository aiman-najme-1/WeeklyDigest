function renderParagraphs(text) {
  return text
    .split(/\n+/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean)
    .map((paragraph) => <p key={paragraph}>{paragraph}</p>);
}

export default function DigestPanel({ digest, labels, metadata }) {
  if (!digest) {
    return (
      <section className="digest-panel digest-panel--empty">
        <p className="section-kicker">{labels.emptyKicker}</p>
        <h2>{labels.emptyTitle}</h2>
        <p>{labels.emptyDescription}</p>
      </section>
    );
  }

  return (
    <section className="digest-panel">
      <p className="section-kicker">{labels.readyKicker}</p>
      <h2>{labels.readyTitle}</h2>
      {metadata && (
        <div className="digest-panel__meta">
          <span>
            {labels.updatedAt}: {metadata.updatedAt || "-"}
          </span>
          <span>
            {labels.resultSource}: {metadata.resultSource || "-"}
          </span>
          <span>
            {labels.sourcesUsed}: {metadata.sourcesUsed || "-"}
          </span>
        </div>
      )}
      <div className="digest-panel__text">{renderParagraphs(digest)}</div>
    </section>
  );
}

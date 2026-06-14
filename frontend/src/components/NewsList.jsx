export default function NewsList({
  articles,
  canSave = false,
  kicker,
  labels = {},
  onSaveArticle,
  savedArticleUrls = [],
  title,
}) {
  if (!articles?.length) {
    return null;
  }

  const sourceLabel = labels.source || "Source";
  const dateLabel = labels.date || "Date";
  const unknownSource = labels.unknownSource || "Unknown source";
  const saveLabel = labels.saveArticle || "Save article";
  const savedLabel = labels.savedArticle || "Saved";

  return (
    <section className="news-list">
      <div className="news-list__header">
        <p className="section-kicker">{kicker}</p>
        <h2>{title}</h2>
      </div>

      <div className="news-list__items">
        {articles.map((article) => {
          const isSaved = savedArticleUrls.includes(article.url);

          return (
            <div className="source-link" key={article.url}>
              <a href={article.url} target="_blank" rel="noreferrer">
                <span>{article.title}</span>
              </a>
              <small>
                {sourceLabel}: {article.source || unknownSource}
              </small>
              {(article.publishedAt || article.published) && (
                <small>
                  {dateLabel}: {article.publishedAt || article.published}
                </small>
              )}
              {canSave && (
                <button
                  type="button"
                  className="ghost-button source-link__save"
                  disabled={isSaved}
                  onClick={() => onSaveArticle(article)}
                >
                  {isSaved ? savedLabel : saveLabel}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

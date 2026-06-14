import { useEffect, useState } from "react";

export default function Cabinet({
  categories,
  languages,
  labels,
  onDeleteSavedArticle,
  onLogout,
  onSavePreferences,
  preferences,
  savedArticles,
  user,
}) {
  const [language, setLanguage] = useState(preferences?.language || "ru");
  const [category, setCategory] = useState(preferences?.category || "sports");

  useEffect(() => {
    setLanguage(preferences?.language || "ru");
    setCategory(preferences?.category || "sports");
  }, [preferences]);

  function handlePreferencesSubmit(event) {
    event.preventDefault();
    onSavePreferences({ language, category });
  }

  return (
    <section className="account-panel">
      <div className="account-panel__header">
        <p className="section-kicker">{labels.kicker}</p>
        <h2>{labels.title}</h2>
      </div>

      <div className="cabinet-user">
        <strong>{user.username}</strong>
        <span>{user.email}</span>
      </div>

      <form className="auth-form" onSubmit={handlePreferencesSubmit}>
        <label>
          {labels.preferredLanguage}
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
          >
            {languages.map((item) => (
              <option key={item.code} value={item.code}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          {labels.preferredCategory}
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            {categories.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </select>
        </label>

        <button type="submit" className="primary-button">
          {labels.savePreferences}
        </button>
      </form>

      <div className="saved-articles">
        <h3>{labels.savedArticles}</h3>
        {!savedArticles.length && <p>{labels.noSavedArticles}</p>}
        {savedArticles.map((article) => (
          <div className="saved-article" key={article.id}>
            <a href={article.url} target="_blank" rel="noreferrer">
              {article.title}
            </a>
            <small>{article.source}</small>
            <button
              type="button"
              className="ghost-button"
              onClick={() => onDeleteSavedArticle(article.id)}
            >
              {labels.deleteArticle}
            </button>
          </div>
        ))}
      </div>

      <button
        type="button"
        className="ghost-button account-panel__switch"
        onClick={onLogout}
      >
        {labels.logout}
      </button>
    </section>
  );
}

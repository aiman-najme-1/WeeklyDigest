export default function LanguageSwitcher({ languages, selectedLanguage, labels, onSelect }) {
  return (
    <section className="toolbar" aria-label={labels.ariaLabel}>
      <div>
        <p className="section-kicker">{labels.kicker}</p>
        <h2>{labels.title}</h2>
      </div>

      <div className="language-switcher">
        {languages.map((language) => (
          <button
            type="button"
            key={language.code}
            className={`language-switcher__item ${
              selectedLanguage === language.code ? "is-active" : ""
            }`}
            disabled={language.disabled}
            onClick={() => onSelect(language.code)}
          >
            <span>{language.label}</span>
            {language.badge && <small>{language.badge}</small>}
          </button>
        ))}
      </div>
    </section>
  );
}

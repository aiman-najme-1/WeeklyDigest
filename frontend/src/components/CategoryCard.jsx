export default function CategoryCard({
  category,
  isSelected,
  isLoading,
  labels,
  onSelect,
  onGenerate,
}) {
  const cardClass = [
    "category-card",
    "category-card--active",
    isSelected ? "is-selected" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <article className={cardClass}>
      <div className="category-card__top">
        <div className="category-card__mark" aria-hidden="true">
          {category.shortName}
        </div>
        <span className="status status--active">{labels.active}</span>
      </div>

      <div>
        <h3>{category.title}</h3>
        <p>{category.description}</p>
      </div>

      <button
        type="button"
        className="primary-button"
        disabled={isLoading}
        onClick={() => {
          onSelect(category.id);
          onGenerate(category.id);
        }}
      >
        {isLoading ? labels.loading : labels.generate}
      </button>
    </article>
  );
}

import { useEffect, useMemo, useState } from "react";

import {
  deleteSavedArticle,
  fetchDigest,
  fetchMe,
  fetchPreferences,
  fetchSavedArticles,
  loginUser,
  registerUser,
  saveArticle,
  updatePreferences,
} from "./api.js";
import AuthPanel from "./components/AuthPanel.jsx";
import Cabinet from "./components/Cabinet.jsx";
import CategoryCard from "./components/CategoryCard.jsx";
import DigestPanel from "./components/DigestPanel.jsx";
import ErrorBox from "./components/ErrorBox.jsx";
import Header from "./components/Header.jsx";
import LanguageSwitcher from "./components/LanguageSwitcher.jsx";
import LoadingState from "./components/LoadingState.jsx";
import NewsList from "./components/NewsList.jsx";

const languages = [
  {
    code: "ru",
    label: "Русский",
    badge: "RU",
  },
  {
    code: "en",
    label: "English",
    badge: "EN",
  },
  {
    code: "ar",
    label: "العربية",
    badge: "AR",
  },
];

const categorySettings = [
  {
    id: "sports",
    shortName: "SP",
  },
  {
    id: "economy",
    shortName: "EC",
  },
  {
    id: "science",
    shortName: "SC",
  },
  {
    id: "technology",
    shortName: "TC",
  },
];

function formatDisplayDate(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

const copy = {
  ru: {
    header: {
      eyebrow: "AI-дайджест новостей",
      subtitle: "Еженедельные новости, кратко и понятно",
      description:
        "Платформа собирает свежие материалы из RSS-источников и превращает их в связный дайджест для быстрого обзора главных событий недели.",
      stats: [
        ["RU / EN / AR", "3 языка"],
        ["4 темы", "рабочие категории"],
        ["RSS", "источники новостей"],
      ],
      statsLabel: "Возможности MVP",
    },
    languageSwitcher: {
      ariaLabel: "Выбор языка интерфейса",
      kicker: "Язык",
      title: "Язык интерфейса",
    },
    categoriesKicker: "Категории",
    categoriesTitle: "Выберите направление дайджеста",
    categoryStatusActive: "Доступно",
    categoryButton: "Создать дайджест",
    categoryLoading: "Готовим...",
    loadingTitle: "Готовим дайджест: ",
    loadingDescription: "Собираем новости из RSS и создаем краткое резюме.",
    errorKicker: "Ошибка",
    errorTitle: "Не удалось создать дайджест. Попробуйте позже.",
    digestEmptyKicker: "Результат",
    digestEmptyTitle: "Дайджест появится здесь",
    digestEmptyDescription:
      "Выберите язык и категорию, чтобы увидеть краткий обзор со ссылками на источники.",
    digestReadyKicker: "Готовый материал",
    digestTitle: "Еженедельный дайджест: ",
    sourcesAriaLabel: "Источники дайджеста",
    newsKicker: "RSS",
    newsTitle: "Новости для дайджеста",
    sourcesKicker: "Источники",
    sourcesPlaceholderTitle: "Ссылки появятся после генерации",
    sourcesPlaceholderDescription:
      "После создания дайджеста здесь будут показаны статьи, которые использовал backend.",
    metadata: {
      updatedAt: "Обновлено",
      resultSource: "Источник данных",
      sourcesUsed: "Использованные источники",
      cache: "кэш",
      fresh: "свежий RSS",
    },
    articleLabels: {
      source: "Источник",
      date: "Дата",
      unknownSource: "Неизвестный источник",
    },
    categories: {
      sports: {
        title: "Спорт",
        description: "Обзор спортивных новостей из актуальных RSS-лент.",
      },
      economy: {
        title: "Экономика",
        description: "Краткий обзор финансовых, деловых и экономических событий.",
      },
      science: {
        title: "Наука",
        description: "Новости исследований, открытий, космоса и научных тем.",
      },
      technology: {
        title: "Технологии",
        description: "Технологические новости, гаджеты, софт и AI-тренды.",
      },
    },
  },
  en: {
    header: {
      eyebrow: "AI-powered weekly news digest",
      subtitle: "Weekly news, short and clear",
      description:
        "The platform collects fresh stories from RSS sources and turns them into a clear digest for a quick review of the week's main events.",
      stats: [
        ["RU / EN / AR", "3 languages"],
        ["4 topics", "working categories"],
        ["RSS", "news sources"],
      ],
      statsLabel: "MVP features",
    },
    languageSwitcher: {
      ariaLabel: "Interface language selection",
      kicker: "Language",
      title: "Interface language",
    },
    categoriesKicker: "Categories",
    categoriesTitle: "Choose a digest topic",
    categoryStatusActive: "Available",
    categoryButton: "Create digest",
    categoryLoading: "Preparing...",
    loadingTitle: "Preparing digest: ",
    loadingDescription: "Collecting RSS news and creating a short summary.",
    errorKicker: "Error",
    errorTitle: "Failed to create digest. Please try again later.",
    digestEmptyKicker: "Result",
    digestEmptyTitle: "The digest will appear here",
    digestEmptyDescription:
      "Choose a language and category to see a short overview with source links.",
    digestReadyKicker: "Ready material",
    digestTitle: "Weekly digest: ",
    sourcesAriaLabel: "Digest sources",
    newsKicker: "RSS",
    newsTitle: "News used for the digest",
    sourcesKicker: "Sources",
    sourcesPlaceholderTitle: "Links will appear after generation",
    sourcesPlaceholderDescription:
      "After creating a digest, this area will show the articles used by the backend.",
    metadata: {
      updatedAt: "Updated at",
      resultSource: "Source",
      sourcesUsed: "Sources used",
      cache: "cache",
      fresh: "fresh RSS",
    },
    articleLabels: {
      source: "Source",
      date: "Date",
      unknownSource: "Unknown source",
    },
    categories: {
      sports: {
        title: "Sports",
        description: "Weekly review of sports news from active RSS feeds.",
      },
      economy: {
        title: "Economy",
        description: "Short review of financial, business, and economic events.",
      },
      science: {
        title: "Science",
        description: "Research, discoveries, space, and science news in one digest.",
      },
      technology: {
        title: "Technology",
        description: "Technology news, gadgets, software, and AI trends.",
      },
    },
  },
  ar: {
    header: {
      eyebrow: "ملخص أخبار أسبوعي بالذكاء الاصطناعي",
      subtitle: "أخبار أسبوعية مختصرة وواضحة",
      description:
        "تجمع المنصة الأخبار من مصادر RSS وتحولها إلى ملخص واضح مع روابط للمقالات الأصلية.",
      stats: [
        ["RU / EN / AR", "3 لغات"],
        ["4 مواضيع", "تصنيفات متاحة"],
        ["RSS", "مصادر أخبار"],
      ],
      statsLabel: "ميزات المشروع",
    },
    languageSwitcher: {
      ariaLabel: "اختيار لغة الواجهة",
      kicker: "اللغة",
      title: "لغة الواجهة",
    },
    categoriesKicker: "التصنيفات",
    categoriesTitle: "اختر موضوع الملخص",
    categoryStatusActive: "متاح",
    categoryButton: "إنشاء الملخص",
    categoryLoading: "جاري التحضير...",
    loadingTitle: "جاري تحضير الملخص: ",
    loadingDescription: "نجمع الأخبار من RSS وننشئ ملخصا قصيرا.",
    errorKicker: "خطأ",
    errorTitle: "تعذر إنشاء الملخص. حاول مرة أخرى لاحقا.",
    digestEmptyKicker: "النتيجة",
    digestEmptyTitle: "سيظهر الملخص هنا",
    digestEmptyDescription:
      "اختر اللغة والتصنيف لعرض ملخص قصير مع روابط المصادر.",
    digestReadyKicker: "الملخص جاهز",
    digestTitle: "الملخص الأسبوعي: ",
    sourcesAriaLabel: "مصادر الملخص",
    newsKicker: "RSS",
    newsTitle: "الأخبار المستخدمة في الملخص",
    sourcesKicker: "المصادر",
    sourcesPlaceholderTitle: "ستظهر الروابط بعد إنشاء الملخص",
    sourcesPlaceholderDescription:
      "بعد إنشاء الملخص ستظهر هنا المقالات التي استخدمها backend.",
    metadata: {
      updatedAt: "آخر تحديث",
      resultSource: "مصدر البيانات",
      sourcesUsed: "المصادر المستخدمة",
      cache: "ذاكرة التخزين",
      fresh: "RSS جديد",
    },
    articleLabels: {
      source: "المصدر",
      date: "التاريخ",
      unknownSource: "مصدر غير معروف",
    },
    categories: {
      sports: {
        title: "الرياضة",
        description: "ملخص أسبوعي لأخبار الرياضة من مصادر RSS.",
      },
      economy: {
        title: "الاقتصاد",
        description: "ملخص قصير للأخبار الاقتصادية والمالية.",
      },
      science: {
        title: "العلوم",
        description: "أخبار الأبحاث والاكتشافات والعلوم.",
      },
      technology: {
        title: "التكنولوجيا",
        description: "أخبار التكنولوجيا والبرمجيات والذكاء الاصطناعي.",
      },
    },
  },
};

const accountCopy = {
  ru: {
    kicker: "Аккаунт",
    loginTitle: "Вход",
    registerTitle: "Регистрация",
    username: "Имя пользователя",
    email: "Email",
    password: "Пароль",
    loginButton: "Войти",
    registerButton: "Зарегистрироваться",
    showLogin: "Уже есть аккаунт? Войти",
    showRegister: "Создать аккаунт",
    title: "Личный кабинет",
    preferredLanguage: "Предпочитаемый язык",
    preferredCategory: "Предпочитаемая категория",
    savePreferences: "Сохранить настройки",
    savedArticles: "Сохраненные статьи",
    noSavedArticles: "Пока нет сохраненных статей.",
    deleteArticle: "Удалить",
    logout: "Выйти",
    saveArticle: "Сохранить статью",
    savedArticle: "Сохранено",
  },
  en: {
    kicker: "Account",
    loginTitle: "Login",
    registerTitle: "Register",
    username: "Username",
    email: "Email",
    password: "Password",
    loginButton: "Login",
    registerButton: "Register",
    showLogin: "Already have an account? Login",
    showRegister: "Create account",
    title: "Personal account",
    preferredLanguage: "Preferred language",
    preferredCategory: "Preferred category",
    savePreferences: "Save preferences",
    savedArticles: "Saved articles",
    noSavedArticles: "No saved articles yet.",
    deleteArticle: "Delete",
    logout: "Logout",
    saveArticle: "Save article",
    savedArticle: "Saved",
  },
  ar: {
    kicker: "الحساب",
    loginTitle: "تسجيل الدخول",
    registerTitle: "إنشاء حساب",
    username: "اسم المستخدم",
    email: "البريد الإلكتروني",
    password: "كلمة المرور",
    loginButton: "دخول",
    registerButton: "تسجيل",
    showLogin: "لديك حساب؟ سجل الدخول",
    showRegister: "إنشاء حساب",
    title: "الحساب الشخصي",
    preferredLanguage: "اللغة المفضلة",
    preferredCategory: "التصنيف المفضل",
    savePreferences: "حفظ التفضيلات",
    savedArticles: "المقالات المحفوظة",
    noSavedArticles: "لا توجد مقالات محفوظة بعد.",
    deleteArticle: "حذف",
    logout: "خروج",
    saveArticle: "حفظ المقال",
    savedArticle: "محفوظ",
  },
};

export default function App() {
  const [selectedLanguage, setSelectedLanguage] = useState("ru");
  const [selectedCategory, setSelectedCategory] = useState("sports");
  const [digestResult, setDigestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingCategory, setLoadingCategory] = useState("");
  const [error, setError] = useState("");
  const [authMode, setAuthMode] = useState("login");
  const [authToken, setAuthToken] = useState(() => localStorage.getItem("weeklydigest_token") || "");
  const [authError, setAuthError] = useState("");
  const [currentUser, setCurrentUser] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [savedArticles, setSavedArticles] = useState([]);

  const text = copy[selectedLanguage];
  const accountText = accountCopy[selectedLanguage];
  const categories = useMemo(
    () =>
      categorySettings.map((category) => ({
        ...category,
        ...text.categories[category.id],
      })),
    [text],
  );

  const selectedCategoryText = text.categories[selectedCategory];
  const resultCategory = digestResult?.category || selectedCategory;
  const resultCategoryText = text.categories[resultCategory] || selectedCategoryText;
  const savedArticleUrls = savedArticles.map((article) => article.url);

  useEffect(() => {
    if (!authToken) {
      setCurrentUser(null);
      setPreferences(null);
      setSavedArticles([]);
      return;
    }

    async function loadAccount() {
      try {
        const [user, userPreferences, articles] = await Promise.all([
          fetchMe(authToken),
          fetchPreferences(authToken),
          fetchSavedArticles(authToken),
        ]);

        setCurrentUser(user);
        setPreferences(userPreferences);
        setSavedArticles(articles);
        setSelectedLanguage(userPreferences.language);
        setSelectedCategory(userPreferences.category);
      } catch (requestError) {
        localStorage.removeItem("weeklydigest_token");
        setAuthToken("");
        setAuthError(requestError.message);
      }
    }

    loadAccount();
  }, [authToken]);

  function handleLanguageSelect(languageCode) {
    setSelectedLanguage(languageCode);
    setDigestResult(null);
    setError("");
  }

  async function handleGenerateDigest(categoryId = selectedCategory) {
    setSelectedCategory(categoryId);
    setIsLoading(true);
    setLoadingCategory(categoryId);
    setError("");
    setDigestResult(null);

    try {
      const result = await fetchDigest(selectedLanguage, categoryId);
      setDigestResult(result);
    } catch (requestError) {
      setError(requestError.message || text.errorTitle);
    } finally {
      setIsLoading(false);
      setLoadingCategory("");
    }
  }

  function saveAuthSession(result) {
    localStorage.setItem("weeklydigest_token", result.token);
    setAuthToken(result.token);
    setCurrentUser(result.user);
    setAuthError("");
  }

  async function handleLogin(data) {
    try {
      const result = await loginUser(data);
      saveAuthSession(result);
    } catch (requestError) {
      setAuthError(requestError.message);
    }
  }

  async function handleRegister(data) {
    try {
      const result = await registerUser(data);
      saveAuthSession(result);
    } catch (requestError) {
      setAuthError(requestError.message);
    }
  }

  function handleLogout() {
    localStorage.removeItem("weeklydigest_token");
    setAuthToken("");
    setCurrentUser(null);
    setPreferences(null);
    setSavedArticles([]);
  }

  async function handleSavePreferences(nextPreferences) {
    try {
      const result = await updatePreferences(authToken, nextPreferences);
      setPreferences(result);
      setSelectedLanguage(result.language);
      setSelectedCategory(result.category);
    } catch (requestError) {
      setAuthError(requestError.message);
    }
  }

  async function handleSaveArticle(article) {
    try {
      const savedArticle = await saveArticle(authToken, {
        title: article.title,
        url: article.url,
        source: article.source,
        published_at: article.publishedAt || article.published || "",
      });
      setSavedArticles((current) => {
        if (current.some((item) => item.url === savedArticle.url)) {
          return current;
        }

        return [savedArticle, ...current];
      });
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleDeleteSavedArticle(articleId) {
    try {
      await deleteSavedArticle(authToken, articleId);
      setSavedArticles((current) => current.filter((article) => article.id !== articleId));
    } catch (requestError) {
      setAuthError(requestError.message);
    }
  }

  return (
    <main className={`app-shell ${selectedLanguage === "ar" ? "is-rtl" : ""}`} dir={selectedLanguage === "ar" ? "rtl" : "ltr"}>
      <Header content={text.header} />

      <LanguageSwitcher
        languages={languages}
        selectedLanguage={selectedLanguage}
        labels={text.languageSwitcher}
        onSelect={handleLanguageSelect}
      />

      {currentUser ? (
        <Cabinet
          categories={categories}
          languages={languages}
          labels={accountText}
          onDeleteSavedArticle={handleDeleteSavedArticle}
          onLogout={handleLogout}
          onSavePreferences={handleSavePreferences}
          preferences={preferences}
          savedArticles={savedArticles}
          user={currentUser}
        />
      ) : (
        <AuthPanel
          error={authError}
          labels={accountText}
          mode={authMode}
          onLogin={handleLogin}
          onModeChange={setAuthMode}
          onRegister={handleRegister}
        />
      )}

      <section className="categories-section">
        <div className="section-heading">
          <p className="section-kicker">{text.categoriesKicker}</p>
          <h2>{text.categoriesTitle}</h2>
        </div>

        <div className="category-grid">
          {categories.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              isSelected={selectedCategory === category.id}
              isLoading={isLoading && loadingCategory === category.id}
              onSelect={setSelectedCategory}
              onGenerate={handleGenerateDigest}
              labels={{
                active: text.categoryStatusActive,
                generate: text.categoryButton,
                loading: text.categoryLoading,
              }}
            />
          ))}
        </div>
      </section>

      <section className="workspace-grid">
        <div className="workspace-grid__main">
          {isLoading && (
            <LoadingState
              title={`${text.loadingTitle}${selectedCategoryText.title}`}
              description={text.loadingDescription}
            />
          )}
          {!isLoading && (
            <ErrorBox kicker={text.errorKicker} title={text.errorTitle} message={error} />
          )}
          {!isLoading && !error && (
            <DigestPanel
              digest={digestResult?.digest}
              labels={{
                emptyKicker: text.digestEmptyKicker,
                emptyTitle: text.digestEmptyTitle,
                emptyDescription: text.digestEmptyDescription,
                readyKicker: text.digestReadyKicker,
                readyTitle: `${text.digestTitle}${resultCategoryText.title}`,
                updatedAt: text.metadata.updatedAt,
                resultSource: text.metadata.resultSource,
                sourcesUsed: text.metadata.sourcesUsed,
              }}
              metadata={
                digestResult
                  ? {
                      updatedAt: formatDisplayDate(digestResult.generatedAt),
                      resultSource: digestResult.fromCache ? text.metadata.cache : text.metadata.fresh,
                      sourcesUsed: digestResult.sourcesUsed?.join(", "),
                    }
                  : null
              }
            />
          )}
        </div>

        <aside className="workspace-grid__side" aria-label={text.sourcesAriaLabel}>
          <NewsList
            articles={digestResult?.articles}
            canSave={Boolean(currentUser)}
            kicker={text.newsKicker}
            labels={{
              source: text.articleLabels.source,
              date: text.articleLabels.date,
              saveArticle: accountText.saveArticle,
              savedArticle: accountText.savedArticle,
              unknownSource: text.articleLabels.unknownSource,
            }}
            onSaveArticle={handleSaveArticle}
            savedArticleUrls={savedArticleUrls}
            title={`${text.newsTitle}: ${resultCategoryText.title}`}
          />
          {!digestResult?.articles?.length && (
            <section className="source-placeholder">
              <p className="section-kicker">{text.sourcesKicker}</p>
              <h2>{text.sourcesPlaceholderTitle}</h2>
              <p>{text.sourcesPlaceholderDescription}</p>
            </section>
          )}
        </aside>
      </section>
    </main>
  );
}

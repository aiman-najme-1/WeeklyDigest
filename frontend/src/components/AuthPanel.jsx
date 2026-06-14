import { useState } from "react";

export default function AuthPanel({
  labels,
  mode,
  onModeChange,
  onLogin,
  onRegister,
  error,
}) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const isRegister = mode === "register";

  async function handleSubmit(event) {
    event.preventDefault();

    if (isRegister) {
      await onRegister({ username, email, password });
    } else {
      await onLogin({ email, password });
    }

    setPassword("");
  }

  return (
    <section className="account-panel">
      <div className="account-panel__header">
        <p className="section-kicker">{labels.kicker}</p>
        <h2>{isRegister ? labels.registerTitle : labels.loginTitle}</h2>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        {isRegister && (
          <label>
            {labels.username}
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>
        )}

        <label>
          {labels.email}
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>

        <label>
          {labels.password}
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {error && <p className="account-panel__error">{error}</p>}

        <button type="submit" className="primary-button">
          {isRegister ? labels.registerButton : labels.loginButton}
        </button>
      </form>

      <button
        type="button"
        className="ghost-button account-panel__switch"
        onClick={() => onModeChange(isRegister ? "login" : "register")}
      >
        {isRegister ? labels.showLogin : labels.showRegister}
      </button>
    </section>
  );
}

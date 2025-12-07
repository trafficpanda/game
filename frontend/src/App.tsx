import React from "react";
import ReactDOM from "react-dom/client";

const App: React.FC = () => {
  return (
    <div style={{ color: "#fff", background: "#000", minHeight: "100vh", padding: 16 }}>
      <h1>Traffic Panda skeleton</h1>
      <p>Минимальный каркас фронтенда. Логика игры будет добавлена поверх.</p>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

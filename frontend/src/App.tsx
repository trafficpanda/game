import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";

// ===================== CONFIG ===========================

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


// ===================== TYPES =============================

type Profile = {
  user_id: number;
  username: string | null;
  coins: number;
  xp: number;
  hourly_income: number;
  level: number;
  rank_name: string;
  rating_score: number;
  avatar_url: string;
  owned_pandas: string[];
  achievements_count: number;
};

type PandaItem = {
  id: string;
  name: string;
  price: number;
  income_bonus: number;
  description: string;
  image_url: string;
  owned: boolean;
  can_afford: boolean;
};

type ShopResponse = {
  items: PandaItem[];
  coins: number;
  hourly_income: number;
};

type Task = {
  id: string;
  title: string;
  description: string;
  reward_xp: number;
  reward_coins: number;
  type: string;
  is_completed: boolean;
};

type TasksResponse = { items: Task[] };

type CourseStep = {
  id: string;
  module_id: string;
  title: string;
  content: string;
  question: string;
  options: string[];
};

type CourseProgress = {
  completed_step_ids: string[];
  next_step: CourseStep | null;
  total_steps: number;
};

type RatingUser = {
  user_id: number;
  username: string | null;
  level: number;
  rank_name: string;
  rating_score: number;
};

type StoryChapter = {
  id: string;
  day: number;
  title: string;
  text: string;
};

type Skill = {
  id: string;
  branch: string;
  name: string;
  description: string;
  level_required: number;
};

type StarsProduct = {
  id: string;
  name_ru: string;
  name_en: string;
  stars_price: number;
  type: string;
  payload: string;
};

type FriendsData = {
  referrals_count: number;
  referral_link: string | null;
};

type Tab =
  | "profile"
  | "shop"
  | "tasks"
  | "learn"
  | "skills"
  | "story"
  | "rating"
  | "friends"
  | "premium";

// ===================== TELEGRAM USER =========================

function getTelegramUserId(): number | null {
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.initDataUnsafe?.user?.id) return tg.initDataUnsafe.user.id;

  const q = new URLSearchParams(window.location.search);
  if (q.get("user_id")) return Number(q.get("user_id"));

  return null;
}

// ===================== MAIN APP ==============================

const App: React.FC = () => {
  const [tab, setTab] = useState<Tab>("profile");

  const [userId, setUserId] = useState<number | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [shop, setShop] = useState<ShopResponse | null>(null);
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [course, setCourse] = useState<CourseProgress | null>(null);
  const [rating, setRating] = useState<RatingUser[] | null>(null);
  const [story, setStory] = useState<StoryChapter[] | null>(null);
  const [skills, setSkills] = useState<Skill[] | null>(null);
  const [friends, setFriends] = useState<FriendsData | null>(null);
  const [products, setProducts] = useState<StarsProduct[] | null>(null);

  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);
  const [buying, setBuying] = useState<string | null>(null);
  const [answering, setAnswering] = useState(false);

  // ============================================================
  // Load everything
  // ============================================================

  useEffect(() => {
    const id = getTelegramUserId();
    if (!id) {
      setToast("Не удалось получить user_id — MiniApp должен запускаться из Telegram.");
      setLoading(false);
      return;
    }

    setUserId(id);

    async function loadAll() {
      try {
        const [
          pRes,
          shRes,
          tRes,
          cRes,
          rRes,
          sRes,
          skRes,
          frRes,
          prRes,
        ] = await Promise.all([
          axios.get<Profile>(`${API_BASE}/profile/${id}`),
          axios.get<ShopResponse>(`${API_BASE}/shop/pandas/${id}`),
          axios.get<TasksResponse>(`${API_BASE}/tasks/${id}`),
          axios.get<CourseProgress>(`${API_BASE}/course-progress/${id}`),
          axios.get<{ items: RatingUser[] }>(`${API_BASE}/rating`),
          axios.get<{ items: StoryChapter[] }>(`${API_BASE}/story/${id}`),
          axios.get<{ items: Skill[] }>(`${API_BASE}/skills/${id}`),
          axios.get<FriendsData>(`${API_BASE}/friends/${id}`),
          axios.get<{ items: StarsProduct[] }>(`${API_BASE}/stars/products`),
        ]);

        setProfile(pRes.data);
        setShop(shRes.data);
        setTasks(tRes.data.items);
        setCourse(cRes.data);
        setRating(rRes.data.items);
        setStory(sRes.data.items);
        setSkills(skRes.data.items);
        setFriends(frRes.data);
        setProducts(prRes.data.items);
      } catch (err) {
        console.error(err);
        setToast("Ошибка загрузки данных");
      } finally {
        setLoading(false);
      }
    }

    loadAll();
  }, []);

  // ============================================================
  // Shop buy
  // ============================================================

  async function buy(pandaId: string) {
    if (!userId) return;
    setBuying(pandaId);
    try {
      await axios.post(`${API_BASE}/shop/buy`, {
        user_id: userId,
        panda_id: pandaId,
      });
      const [pRes, shRes] = await Promise.all([
        axios.get<Profile>(`${API_BASE}/profile/${userId}`),
        axios.get<ShopResponse>(`${API_BASE}/shop/pandas/${userId}`),
      ]);
      setProfile(pRes.data);
      setShop(shRes.data);
      setToast("Панда куплена! 🐼");
    } catch (e: any) {
      setToast(e.response?.data?.detail || "Ошибка покупки");
    } finally {
      setBuying(null);
    }
  }

  // ============================================================
  // Answer course step
  // ============================================================

  async function answerCourse(optionIndex: number) {
    if (!userId || !course?.next_step) return;
    setAnswering(true);
    try {
      const res = await axios.post(`${API_BASE}/course/answer`, {
        user_id: userId,
        step_id: course.next_step.id,
        answer_index: optionIndex,
      });

      setToast(res.data.message);
      setProfile(res.data.profile);
      setCourse(res.data.course_progress);

      // refresh story
      const st = await axios.get<{ items: StoryChapter[] }>(
        `${API_BASE}/story/${userId}`
      );
      setStory(st.data.items);
    } catch (e: any) {
      setToast(e.response?.data?.detail || "Ошибка ответа");
    } finally {
      setAnswering(false);
    }
  }

  // ============================================================
  // UI COMPONENTS
  // ============================================================

  if (loading) {
    return <div style={screenStyle}>Загрузка Traffic Panda…</div>;
  }

  if (!profile) {
    return <div style={screenStyle}>{toast || "Ошибка профиля"}</div>;
  }

  const completed = course?.completed_step_ids?.length || 0;
  const total = course?.total_steps || 0;
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

  function SectionTitle({ children }: { children: React.ReactNode }) {
    return (
      <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 10 }}>
        {children}
      </div>
    );
  }

  // ================= TABS =====================

  function ProfileTab() {
    return (
      <>
        <SectionTitle>Твоя Панда</SectionTitle>

        <div style={{ textAlign: "center", marginBottom: 12 }}>
          <img
            src={profile.avatar_url}
            style={{
              width: "60%",
              height: "auto",
              borderRadius: 20,
              boxShadow: "0 0 12px #444",
            }}
          />
        </div>

        <div style={card}>
          <b>Уровень:</b> {profile.level} • {profile.rank_name}
          <br />
          <b>XP:</b> {profile.xp}
          <br />
          <b>Баланс:</b> {profile.coins.toLocaleString()} 🪙
          <br />
          <b>Доход в час:</b> {profile.hourly_income} 🪙
        </div>

        <div style={card}>
          <b>Прогресс обучения:</b> {completed}/{total} ({pct}%)
          <div style={progressBar}>
            <div style={{ ...progressFill, width: pct + "%" }} />
          </div>
        </div>

        <div style={card}>
          <b>Ачивки:</b> {profile.achievements_count}
        </div>
      </>
    );
  }

  function ShopTab() {
    if (!shop) return null;
    return (
      <>
        <SectionTitle>Магазин панд</SectionTitle>
        {shop.items.map((p) => (
          <div key={p.id} style={card}>
            <div style={{ display: "flex", gap: 12 }}>
              <img
                src={p.image_url}
                style={{
                    width: "100%",
                    height: "auto",
                    borderRadius: 10,
                    display: "block",
                }}
              />
              <div>
                <b>{p.name}</b>
                <br />
                {p.description}
                <br />
                +{p.income_bonus} / час
                <br />
                <b>{p.price.toLocaleString()} 🪙</b>
              </div>
            </div>
            <div style={{ marginTop: 8 }}>
              {p.owned ? (
                <span>✔ Куплено</span>
              ) : (
                <button
                  disabled={!p.can_afford || buying === p.id}
                  onClick={() => buy(p.id)}
                  style={buttonStyle}
                >
                  {buying === p.id ? "..." : "Купить"}
                </button>
              )}
            </div>
          </div>
        ))}
      </>
    );
  }

  function TasksTab() {
    if (!tasks) return null;
    return (
      <>
        <SectionTitle>Задания</SectionTitle>
        {tasks.map((t) => (
          <div key={t.id} style={card}>
            <b>{t.title}</b>
            <br />
            {t.description}
            <br />
            Награда: +{t.reward_xp} XP • {t.reward_coins.toLocaleString()} 🪙
          </div>
        ))}
      </>
    );
  }

  function LearnTab() {
    return (
      <>
        <SectionTitle>Обучение</SectionTitle>

        <div style={card}>
          Прогресс: {completed}/{total} ({pct}%)
          <div style={progressBar}>
            <div style={{ ...progressFill, width: pct + "%" }} />
          </div>
        </div>

        {course?.next_step ? (
          <div style={card}>
            <div style={{ fontSize: 18, fontWeight: 600 }}>
              {course.next_step.title}
            </div>

            <div style={{ marginTop: 8, whiteSpace: "pre-line" }}>
              {course.next_step.content}
            </div>

            <div style={{ marginTop: 12, fontWeight: 600 }}>
              {course.next_step.question}
            </div>

            {course.next_step.options.map((opt, idx) => (
              <button
                key={idx}
                disabled={answering}
                style={buttonStyle}
                onClick={() => answerCourse(idx)}
              >
                {opt}
              </button>
            ))}
          </div>
        ) : (
          <div style={card}>Все уроки пройдены! 🎓🐼</div>
        )}
      </>
    );
  }

  function SkillsTab() {
    if (!skills) return null;
    return (
      <>
        <SectionTitle>Навыки</SectionTitle>
        {skills.map((s) => (
          <div key={s.id} style={card}>
            <b>{s.name}</b> ({s.branch})
            <br />
            {s.description}
            <br />
            <span style={{ opacity: 0.7 }}>
              Доступно с уровня {s.level_required}
            </span>
          </div>
        ))}
      </>
    );
  }

  function StoryTab() {
    if (!story) return null;
    return (
      <>
        <SectionTitle>Сюжет</SectionTitle>
        {story.map((c) => (
          <div key={c.id} style={card}>
            <b>
              Глава {c.day}: {c.title}
            </b>
            <br />
            <div style={{ marginTop: 8, whiteSpace: "pre-line" }}>{c.text}</div>
          </div>
        ))}
      </>
    );
  }

  function RatingTab() {
    if (!rating) return null;
    return (
      <>
        <SectionTitle>Рейтинг</SectionTitle>
        {rating.map((u, idx) => (
          <div key={u.user_id} style={card}>
            <b>
              {idx + 1}. {u.username || `ID ${u.user_id}`}
            </b>
            <br />
            {u.rank_name} • lvl {u.level}
            <br />
            Очки: {u.rating_score.toLocaleString()}
          </div>
        ))}
      </>
    );
  }

  function FriendsTab() {
    if (!friends) return null;
    return (
      <>
        <SectionTitle>Друзья</SectionTitle>
        <div style={card}>
          Приглашено друзей: <b>{friends.referrals_count}</b>
          <br />
          <br />
          Твоя ссылka:
          <br />
          <div style={{ wordBreak: "break-all", marginTop: 6 }}>
            {friends.referral_link || "Ссылка появится, когда ты настроишь BOT_USERNAME"}
          </div>
        </div>
      </>
    );
  }

  function PremiumTab() {
    if (!products) return null;
    return (
      <>
        <SectionTitle>Premium ⭐</SectionTitle>
        {products.map((p) => (
          <div key={p.id} style={card}>
            <b>{p.name_ru}</b> — {p.stars_price} ⭐
            <br />
            <span style={{ opacity: 0.8 }}>{p.name_en}</span>
            <br />
            <small>Тип: {p.type}</small>
          </div>
        ))}
        <div style={card}>
          ❗ Покупка Stars через Telegram WebApp включается после подключения invoice.
        </div>
      </>
    );
  }

  function renderTab() {
    switch (tab) {
      case "profile":
        return <ProfileTab />;
      case "shop":
        return <ShopTab />;
      case "tasks":
        return <TasksTab />;
      case "learn":
        return <LearnTab />;
      case "skills":
        return <SkillsTab />;
      case "story":
        return <StoryTab />;
      case "rating":
        return <RatingTab />;
      case "friends":
        return <FriendsTab />;
      case "premium":
        return <PremiumTab />;
      default:
        return null;
    }
  }

  return (
    <div style={screenStyle}>
      <div style={{ padding: 16, width: "100%", maxWidth: 600 }}>
        {renderTab()}
      </div>

      <div style={navBar}>
        <NavButton
          icon="🏠"
          label="Панда"
          active={tab === "profile"}
          onClick={() => setTab("profile")}
        />
        <NavButton
          icon="🐼"
          label="Магазин"
          active={tab === "shop"}
          onClick={() => setTab("shop")}
        />
        <NavButton
          icon="✅"
          label="Задания"
          active={tab === "tasks"}
          onClick={() => setTab("tasks")}
        />
        <NavButton
          icon="🎓"
          label="Обучение"
          active={tab === "learn"}
          onClick={() => setTab("learn")}
        />
        <NavButton
          icon="🧠"
          label="Навыки"
          active={tab === "skills"}
          onClick={() => setTab("skills")}
        />
        <NavButton
          icon="📖"
          label="Сюжет"
          active={tab === "story"}
          onClick={() => setTab("story")}
        />
        <NavButton
          icon="🏆"
          label="Рейтинг"
          active={tab === "rating"}
          onClick={() => setTab("rating")}
        />
        <NavButton
          icon="👥"
          label="Друзья"
          active={tab === "friends"}
          onClick={() => setTab("friends")}
        />
        <NavButton
          icon="⭐"
          label="Premium"
          active={tab === "premium"}
          onClick={() => setTab("premium")}
        />
      </div>

      {toast && (
        <div style={toastStyle} onClick={() => setToast(null)}>
          {toast}
        </div>
      )}
    </div>
  );
};

// ===================== UI HELPERS =============================

const screenStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "#050505",
  color: "#fff",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  paddingBottom: 64,
};

const card: React.CSSProperties = {
  background: "#151515",
  borderRadius: 16,
  padding: 12,
  marginBottom: 10,
  boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
  fontSize: 13,
};

const progressBar: React.CSSProperties = {
  width: "100%",
  height: 6,
  borderRadius: 999,
  background: "#262626",
  marginTop: 6,
  overflow: "hidden",
};

const progressFill: React.CSSProperties = {
  height: "100%",
  background: "linear-gradient(90deg,#ffb300,#ff5c20)",
};

const buttonStyle: React.CSSProperties = {
  marginTop: 6,
  display: "block",
  width: "100%",
  borderRadius: 999,
  border: "none",
  padding: "8px 12px",
  fontSize: 13,
  fontWeight: 600,
  background: "linear-gradient(90deg,#ffb300,#ff5c20)",
  color: "#000",
  cursor: "pointer",
};

const navBar: React.CSSProperties = {
  position: "fixed",
  bottom: 0,
  left: 0,
  right: 0,
  background: "#050505",
  borderTop: "1px solid #222",
  display: "flex",
  justifyContent: "space-around",
  padding: "6px 4px 10px",
  fontSize: 11,
};

const toastStyle: React.CSSProperties = {
  position: "fixed",
  bottom: 72,
  left: 0,
  right: 0,
  margin: "0 auto",
  maxWidth: 400,
  background: "#222",
  borderRadius: 999,
  padding: "8px 14px",
  textAlign: "center",
  fontSize: 12,
  cursor: "pointer",
};

type NavProps = {
  icon: string;
  label: string;
  active: boolean;
  onClick: () => void;
};

const NavButton: React.FC<NavProps> = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    style={{
      background: "none",
      border: "none",
      color: active ? "#ffb300" : "#aaa",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 2,
      cursor: "pointer",
    }}
  >
    <span style={{ fontSize: 18 }}>{icon}</span>
    <span>{label}</span>
  </button>
);

// ===================== RENDER ================================

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

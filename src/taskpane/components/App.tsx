import * as React from "react";
import { useState, useEffect } from "react";
import Header from "./Header";
import { makeStyles } from "@fluentui/react-components";
import FormulaGenerator from "./FormulaGenerator";
import FormulaExplainer from "./FormulaExplainer";
import Auth from "./Auth";

const useStyles = makeStyles({
  root: {
    minHeight: "100vh",
    background: "#fff",
    display: "flex",
    flexDirection: "column",

    fontFamily: '"Segoe UI", "Microsoft YaHei", Arial, sans-serif',
  },

  tabBar: {
    display: "flex",
    justifyContent: "center",
    borderBottom: "1.5px solid #e0e0e0",
    background: "#fff",
  },
  tab: {
    flex: 1,
    fontSize: "18px",
    fontWeight: 500,
    color: "#222",
    padding: "16px 0",
    background: "none",
    border: "none",
    borderBottom: "3px solid transparent",
    cursor: "pointer",
    transition: "border-color 0.2s, color 0.2s",
  },
  tabActive: {
    borderBottom: "3px solid #1a7f37",
    color: "#1a7f37",
    background: "#f6faf7",
  },
  content: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
    justifyContent: "flex-start",
    padding: 0,
  },
});

type TabValue = "generator" | "explainer";

const App: React.FC = () => {
  const styles = useStyles();
  const [selectedTab, setSelectedTab] = useState<TabValue>("generator");
  const [token, setToken] = useState<string | null>(localStorage.getItem("authToken"));
  const [email, setEmail] = useState<string | null>(null);
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem("authToken", token);
      setEmail("user@example.com"); // TODO: fetch real user info
    } else {
      localStorage.removeItem("authToken");
      setEmail(null);
    }
  }, [token]);

  const onLoginSuccess = (newToken: string) => {
    setToken(newToken);
    setShowAuth(false);
  };

  const handleLogout = () => {
    setToken(null);
    setShowAuth(false);
  };

  return (
    <div className={styles.root}>
        <Header
          loggedIn={!!token}
          email={email || undefined}
          onLogin={() => setShowAuth(true)}
          onLogout={handleLogout}
        />
        <div className={styles.content}>
          {!token || showAuth ? (
            <Auth onLoginSuccess={onLoginSuccess} />
          ) : (
            <>
              <div className={styles.tabBar}>
                <button
                  className={selectedTab === "generator" ? `${styles.tab} ${styles.tabActive}` : styles.tab}
                  onClick={() => setSelectedTab("generator")}
                >
                  生成公式
                </button>
                <button
                  className={selectedTab === "explainer" ? `${styles.tab} ${styles.tabActive}` : styles.tab}
                  onClick={() => setSelectedTab("explainer")}
                >
                  解释公式
                </button>
              </div>
              {selectedTab === "generator" && <FormulaGenerator token={token} />}
              {selectedTab === "explainer" && <FormulaExplainer token={token} />}
            </>
          )}
        </div>
    </div>
  );
};

export default App;

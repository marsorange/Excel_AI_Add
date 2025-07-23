import * as React from "react";
import { useState } from "react";
import { makeStyles } from "@fluentui/react-components";
import { API_ENDPOINTS } from "../../config/api";

const useStyles = makeStyles({
  root: {
    width: "100%",
    margin: "48px auto 0 auto",
    background: "#fff",
    borderRadius: "16px",
    boxShadow: "0 2px 12px 0 rgba(0,0,0,0.06)",
    padding: "0 0 40px 0",
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
  },
  content: {
    padding: "40px 32px 0 32px",
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
  },
  title: {
    fontSize: "28px",
    fontWeight: 700,
    marginBottom: "6px",
    color: "#222",
    lineHeight: 1.2,
  },
  subtitle: {
    fontSize: "18px",
    fontWeight: 400,
    color: "#222",
    marginBottom: "32px",
    lineHeight: 1.5,
  },
  input: {
    
    fontSize: "18px",
    border: "1.5px solid #e0e0e0",
    borderRadius: "10px",
    padding: "16px 16px",
    marginBottom: "18px",
    outline: "none",
    background: "#fafafa",
    color: "#222",
    fontFamily: '"Segoe UI", "Microsoft YaHei", Arial, sans-serif',
    transition: "border 0.2s",
    "::placeholder": {
      color: "#c8c8c8",
      fontWeight: 400,
    },
    ":focus": {
      border: "1.5px solid #1a7f37",
    },
  },
  agreement: {
    color: "#1a7f37",
    fontSize: "15px",
    marginBottom: "12px",
    cursor: "pointer",
    textDecoration: "underline",
    alignSelf: "flex-start",
    marginTop: "-6px",
  },
  button: {
    width: "100%",
    background: "#1a7f37",
    color: "#fff",
    fontSize: "22px",
    fontWeight: 700,
    border: "none",
    borderRadius: "8px",
    padding: "16px 0",
    marginTop: "8px",
    cursor: "pointer",
    transition: "background 0.2s",
    letterSpacing: "2px",
    ":hover": {
      background: "#176c2c",
    },
  },
  error: {
    color: "#d32f2f",
    fontSize: "15px",
    margin: "8px 0 0 0",
    minHeight: "22px",
  },
  switch: {
    marginTop: "48px",
    fontSize: "15px",
    color: "#bdbdbd",
    textAlign: "left",
    letterSpacing: 0,
  },
  switchLink: {
    color: "#1a7f37",
    marginLeft: "4px",
    cursor: "pointer",
    textDecoration: "underline",
    fontWeight: 500,
  },
});

interface AuthProps {
  onLoginSuccess: (token: string) => void;
}

const Auth: React.FC<AuthProps> = ({ onLoginSuccess }) => {
  const styles = useStyles();
  const [isRegister, setIsRegister] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isRegister) {
        const res = await fetch(API_ENDPOINTS.REGISTER, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "注册失败");
        }
      }
      // 登录
      const loginRes = await fetch(API_ENDPOINTS.LOGIN, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
      });
      if (!loginRes.ok) {
        const err = await loginRes.json();
        throw new Error(err.detail || "登录失败");
      }
      const data = await loginRes.json();
      onLoginSuccess(data.access_token);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (

      <form className={styles.content} onSubmit={handleSubmit}>
        <div className={styles.title}>{isRegister ? "立即注册" : "立即登录"}</div>
        <div className={styles.subtitle}>使用最智能的 Excel 财务助理</div>
        <input
          className={styles.input}
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          autoComplete="username"
          required
        />
        <input
          className={styles.input}
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          autoComplete={isRegister ? "new-password" : "current-password"}
          required
        />
        <div className={styles.agreement}>《用户协议》</div>
        <div className={styles.error}>{error || ""}</div>
        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? (isRegister ? "注册中..." : "登录中...") : (isRegister ? "注册" : "登录")}
        </button>
        <div className={styles.switch}>
          {isRegister ? (
            <>
              已有账号？ 立即
              <span className={styles.switchLink} onClick={() => setIsRegister(false)}>登录</span>
            </>
          ) : (
            <>
              还没有账号？ 立即
              <span className={styles.switchLink} onClick={() => setIsRegister(true)}>注册</span>
            </>
          )}
        </div>
      </form>

  );
};

export default Auth;

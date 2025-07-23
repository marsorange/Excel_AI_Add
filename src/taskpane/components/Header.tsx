import * as React from "react";
import { makeStyles } from "@fluentui/react-components";
// @ts-ignore
import excelLogo from "../../../assets/logo.png";

interface HeaderProps {
  loggedIn: boolean;
  email?: string;
  onLogin: () => void;
  onLogout: () => void;
}

const useStyles = makeStyles({
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: "#fff",
    height: "64px",
    borderBottom: "1.5px solid #1a7f37",
    boxShadow: "none",
    borderRadius: 0,
    margin: 0,
    padding: "0 0 0 0",
  },
  logoTitle: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginLeft: "24px",
  },
  logo: {
    width: "25.25px",
    height: "42px",
    marginRight: "6px",
  },
  title: {
    fontSize: "20px",
    fontWeight: 700,
    color: "#1a7f37",
    fontFamily: '"Segoe UI", "Microsoft YaHei", Arial, sans-serif',
    letterSpacing: "1px",
  },
  userArea: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginRight: "24px"
  },
  email: {
    color: "#888",
    fontSize: "15px",
    fontWeight: 400,
    marginRight: "8px",
    marginleft: "8px",
  },
  btn: {
    background: "#1a7f37",
    color: "#fff",
    fontSize: "15px",
    fontWeight: 500,
    border: "none",
    borderRadius: "6px",
    padding: "6px 18px 6px 18px",
    cursor: "pointer",
    transition: "background 0.2s",
    ":hover": {
      background: "#176c2c",
    },
  },
});

const Header: React.FC<HeaderProps> = ({ loggedIn, email,onLogout }) => {
  const styles = useStyles();
  return (
    <div className={styles.header}>
      <div className={styles.logoTitle}>
        <img src={excelLogo} className={styles.logo} alt="Excel Logo" />
        <span className={styles.title}>财务助手</span>
      </div>
      <div className={styles.userArea}>
        {loggedIn && email ? (
          <>
            <span className={styles.email}>{email}</span>
            <button className={styles.btn} onClick={onLogout}>登出</button>
          </>
        ) : null
      }
      </div>
    </div>
  );
};

export default Header;

import * as React from "react";
import { useState } from "react";
import { Button, Textarea, makeStyles, Spinner, Text } from "@fluentui/react-components";

const useStyles = makeStyles({
  root: {
    display: "flex",
    flexDirection: "column",
    gap: "24px",
    padding: "24px",
  },
  textarea: {
    minHeight: "96px",
    borderRadius: "10px",
    fontSize: "17px",
    background: "#fafafa",
    border: "1.5px solid #e0e0e0",
    marginBottom: "0",
    padding: "16px 14px",
    resize: "none",
    "::placeholder": {
      color: "#bdbdbd",
      fontWeight: 400,
    },
  },
  buttonRow: {
    display: "flex",
    gap: "18px",
    marginTop: "8px",
    marginBottom: "8px",
  },
  btn: {
    flex: 1,
    height: "48px",
    fontSize: "20px",
    fontWeight: 600,
    borderRadius: "8px",
    letterSpacing: "2px",
  },
  btnPrimary: {
    background: "#1a7f37",
    color: "#fff",
    border: "none",
    ":hover": {
      background: "#176c2c",
    },
  },
  btnSecondary: {
    background: "#f5f5f5",
    color: "#222",
    border: "none",
    ":hover": {
      background: "#e0e0e0",
    },
  },

  previewTitle: {
    fontSize: "16px",
    fontWeight: 600,
    color: "#222",
    marginBottom: "6px",
  },
  previewTextarea: {
    minHeight: "56px",
    borderRadius: "8px",
    fontSize: "17px",
    background: "#fff",
    border: "1.5px solid #e0e0e0",
    padding: "12px 12px",
    resize: "none",
    marginBottom: "0",
    color: "#222",
  },
  previewBtnRow: {
    display: "flex",
    gap: "18px",
    marginTop: "12px",
  },

  errorText: {
    color: "#d13438",
    fontSize: "15px",
    marginTop: "4px",
    minHeight: "22px",
  },
});

interface FormulaExplainerProps {
  token: string | null;
}

const FormulaExplainer: React.FC<FormulaExplainerProps> = ({ token }) => {
  const styles = useStyles();
  const [formula, setFormula] = useState("");
  const [explanation, setExplanation] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExplain = async () => {
    if (!token) {
      setError("请先登录");
      return;
    }
    setIsLoading(true);
    setError(null);
    setExplanation("");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/explain-formula", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ formula }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "解释公式失败");
      }
      const data = await response.json();
      setExplanation(data.explanation);
    } catch (err: any) {
      setError(err.message || "网络错误");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFormula("");
    setExplanation("");
    setError(null);
  };

  const handleCopy = () => {
    if (explanation) {
      navigator.clipboard.writeText(explanation);
    }
  };

  return (
    <div className={styles.root}>
      <Textarea
        className={styles.textarea}
        placeholder="输入需要解释的公式"
        value={formula}
        onChange={(e) => setFormula(e.target.value)}
        disabled={isLoading}
      />
      <div className={styles.buttonRow}>
        <Button className={`${styles.btn} ${styles.btnSecondary}`} onClick={handleClear} disabled={isLoading && !formula}>
          清 除
        </Button>
        <Button className={`${styles.btn} ${styles.btnPrimary}`} onClick={handleExplain} disabled={isLoading || !formula.trim()}>
          {isLoading ? <Spinner size="tiny" /> : "解 释"}
        </Button>
      </div>
      <div className={styles.errorText}>{error || ""}</div>
      
        <div className={styles.previewTitle}>解释结果</div>
        <Textarea
          className={styles.previewTextarea}
          readOnly
          value={explanation}
          placeholder="公式的解释会显示在此处"
        />
    </div>
  );
};

export default FormulaExplainer;

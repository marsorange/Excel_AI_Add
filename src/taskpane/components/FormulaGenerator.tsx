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
  previewCard: {
    background: "#fafafa",
    borderRadius: "12px",
    boxShadow: "0 1px 4px 0 rgba(0,0,0,0.04)",
    padding: "18px 18px 12px 18px",
    marginTop: "8px",
    marginBottom: "0",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
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
  previewBtn: {
    flex: 1,
    height: "40px",
    fontSize: "17px",
    fontWeight: 500,
    borderRadius: "8px",
    background: "#f5f5f5",
    color: "#222",
    border: "none",
    ":hover": {
      background: "#e0e0e0",
    },
  },
  errorText: {
    color: "#d13438",
    fontSize: "15px",
    marginTop: "4px",
    minHeight: "22px",
  },
});

interface FormulaGeneratorProps {
  token: string | null;
}

const FormulaGenerator: React.FC<FormulaGeneratorProps> = ({ token }) => {
  const styles = useStyles();
  const [naturalLanguage, setNaturalLanguage] = useState("");
  const [formula, setFormula] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!token) {
      setError("请先登录");
      return;
    }
    setIsLoading(true);
    setError(null);
    setFormula("");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/generate-formula", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ text: naturalLanguage }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "生成公式失败");
      }
      const data = await response.json();
      setFormula(data.formula);
    } catch (err: any) {
      setError(err.message || "网络错误");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setNaturalLanguage("");
    setFormula("");
    setError(null);
  };

  const handleCopy = () => {
    if (formula) {
      navigator.clipboard.writeText(formula);
    }
  };

  return (
    <div className={styles.root}>
      <Textarea
        className={styles.textarea}
        placeholder="直接描述想生成的公式"
        value={naturalLanguage}
        onChange={(e) => setNaturalLanguage(e.target.value)}
        disabled={isLoading}
      />
      <div className={styles.buttonRow}>
        <Button className={`${styles.btn} ${styles.btnSecondary}`} onClick={handleClear} disabled={isLoading && !naturalLanguage}>
          清 除
        </Button>
        <Button className={`${styles.btn} ${styles.btnPrimary}`} onClick={handleGenerate} disabled={isLoading || !naturalLanguage.trim()}>
          {isLoading ? <Spinner size="tiny" /> : "生 成"}
        </Button>
      </div>
      <div className={styles.errorText}>{error || ""}</div>
      
        <div className={styles.previewTitle}>公式预览</div>
        <Textarea
          className={styles.previewTextarea}
          readOnly
          value={formula}
          placeholder="生成的公式将展示在这"
        />
        <div className={styles.previewBtnRow}>
          <Button className={styles.previewBtn} onClick={handleCopy} disabled={!formula}>复制公式</Button>
          <Button className={styles.previewBtn} disabled={!formula}>插入公式</Button>
        </div>
      
    </div>
  );
};

export default FormulaGenerator;

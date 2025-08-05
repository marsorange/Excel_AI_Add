import * as React from "react";
import { useState, useRef, useEffect } from "react";
import {
  makeStyles,
  Button,
  Textarea,
  Text,
  Spinner,
  MessageBar,
  Card,
  tokens,
  mergeClasses
} from "@fluentui/react-components";
import {
  Send24Regular,
  Bot24Regular,
  Play24Regular,
  Copy24Regular,
  CheckmarkCircle24Regular,
  ErrorCircle24Regular,
} from "@fluentui/react-icons";
import { API_ENDPOINTS } from "../../config/api";

/* global Excel, console */

const useStyles = makeStyles({
  root: {
    display: "flex",
    flexDirection: "column",
    height: "100%",
    backgroundColor: tokens.colorNeutralBackground1,
    fontFamily: tokens.fontFamilyBase,
  },
  chatContainer: {
    flexGrow: 1,
    display: "flex",
    flexDirection: "column",
    minHeight: 0,
  },
  messagesArea: {
    flexGrow: 1,
    overflowY: "auto",
    padding: tokens.spacingVerticalL,
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalL,
  },
  message: {
    display: "flex",
    alignItems: "flex-start",
    gap: tokens.spacingHorizontalM,
    maxWidth: "100%",
  },
  userMessage: {
    alignSelf: "flex-end",
    padding: tokens.spacingVerticalM,
    border: `1px solid ${tokens.colorPaletteGreenBorder2}`,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground1,
    maxWidth: "70%",
  },
  agentMessageContainer: {
    alignSelf: "flex-start",
    flexDirection: "column",
    gap: tokens.spacingVerticalS,
    maxWidth: "85%",
  },
  messageContent: {
    flex: 1,
  },
  messageText: {
    fontSize: tokens.fontSizeBase300,
    lineHeight: tokens.lineHeightBase300,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    color: tokens.colorNeutralForeground1,
  },
  operationsContainer: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
    marginTop: tokens.spacingVerticalS,
  },
  operationCard: {
    padding: tokens.spacingVerticalM,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  operationHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: tokens.spacingVerticalS,
  },
  operationTitle: {
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground3,
  },
  codeBlock: {
    backgroundColor: tokens.colorNeutralBackground3,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusSmall,
    padding: tokens.spacingVerticalS,
    fontSize: tokens.fontSizeBase200,
    fontFamily: tokens.fontFamilyMonospace,
    overflow: "auto",
    maxHeight: "150px",
    marginBottom: tokens.spacingVerticalM,
    whiteSpace: "pre-wrap",
  },
  operationActions: {
    display: "flex",
    gap: tokens.spacingHorizontalS,
  },
  executeButton: {
    borderColor: tokens.colorPaletteGreenBorder2,
    color: tokens.colorPaletteGreenForeground1,
  } as any,
  inputArea: {
    padding: tokens.spacingVerticalL,
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  inputContainer: {
    position: "relative",
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    overflow: "hidden",
  },
  inputField: {
    border: "none",
    outline: "none",
    padding: tokens.spacingVerticalM,
    paddingRight: "56px",
    fontSize: tokens.fontSizeBase300,
    backgroundColor: "transparent",
    resize: "none",
    height: "96px",
    fontFamily: tokens.fontFamilyBase,
    width: "100%",
    "::placeholder": {
      color: tokens.colorNeutralForeground3,
    },
  },
  sendButtonContainer: {
    position: "absolute",
    bottom: tokens.spacingVerticalXS,
    right: tokens.spacingHorizontalXS,
    width: "40px",
    height: "40px",
    backgroundColor: tokens.colorPaletteGreenBackground3,
    borderRadius: tokens.borderRadiusSmall,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    border: "none",
    ":hover": {
      backgroundColor: tokens.colorPaletteGreenBackground2,
    },
    ":disabled": {
      backgroundColor: tokens.colorNeutralBackgroundDisabled,
      cursor: "not-allowed",
    },
  } as any,
  loadingContainer: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalS,
    padding: tokens.spacingVerticalL,
  },
  errorMessage: {
    margin: `0 ${tokens.spacingHorizontalL} ${tokens.spacingVerticalM} ${tokens.spacingHorizontalL}`,
  },
  emptyState: {
    textAlign: "center",
    color: tokens.colorNeutralForeground3,
    marginTop: tokens.spacingVerticalXXXL,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: tokens.spacingVerticalM,
  },
  emptyStateIcon: {
    fontSize: "48px",
    color: tokens.colorNeutralForeground3,
    marginBottom: 0,
  },
  avatar: {
    color: tokens.colorBrandForeground1,
    fontSize: "20px",
    flexShrink: 0,
    marginTop: tokens.spacingVerticalXS,
  },
});

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  operations?: ExcelOperation[];
  error?: string;
}

interface ExcelOperation {
  operation_type: string;
  description: string;
  js_code?: string;
  parameters?: any;
}

interface AgentChatProps {
  token: string;
}


const AgentChat: React.FC<AgentChatProps> = ({ token }) => {
  const styles = useStyles();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [executionStatus, setExecutionStatus] = useState<{ [key: string]: 'pending' | 'executing' | 'success' | 'error' }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const addMessage = (type: 'user' | 'agent', content: string, operations?: ExcelOperation[], error?: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      operations,
      error
    };
    setMessages(prev => [...prev, newMessage]);
  };

  // 将二维数组转为 Markdown 表格
  function arrayToMarkdownTable(data: any[][]): string {
    if (!data || data.length === 0) return '';
    const header = data[0];
    const rows = data.slice(1);
    const headerLine = '| ' + header.map(String).join(' | ') + ' |';
    const separator = '| ' + header.map(() => '---').join(' | ') + ' |';
    const rowLines = rows.map(row => '| ' + row.map(cell => (cell === undefined ? '' : String(cell))).join(' | ') + ' |');
    return [headerLine, separator, ...rowLines].join('\n');
  }

  // 从AI回复中提取Excel代码
  function extractExcelCodeFromResponse(response: string): { cleanResponse: string; excelOperations: ExcelOperation[] } {
    const excelOperations: ExcelOperation[] = [];
    
    // 匹配JavaScript代码块（包含Excel.run）
    const codeBlockRegex = /```(?:javascript|js)?\s*\n([\s\S]*?)\n```/g;
    const excelRunRegex = /Excel\.run\s*\(\s*async\s*\(\s*context\s*\)\s*=>\s*\{([\s\S]*?)\}\s*\);?/g;
    
    let cleanResponse = response;
    let match;
    
    // 首先处理代码块中的Excel代码
    while ((match = codeBlockRegex.exec(response)) !== null) {
      const codeBlock = match[1];
      const excelRunMatch = excelRunRegex.exec(codeBlock);
      
      if (excelRunMatch) {
        const excelCode = `Excel.run(async (context) => {${excelRunMatch[1]}});`;
        const description = codeBlock.replace(/[\n\r]+/g, ' ').trim().substring(0, 100) + '...';
        
        excelOperations.push({
          operation_type: 'excel_operation',
          description: description,
          js_code: excelCode
        });
        
        // 从响应中移除代码块
        cleanResponse = cleanResponse.replace(match[0], '');
      }
    }
    
    // 然后处理直接的Excel.run代码（不在代码块中的）
    if (excelOperations.length === 0) {
      while ((match = excelRunRegex.exec(response)) !== null) {
        const excelCode = `Excel.run(async (context) => {${match[1]}});`;
        const description = `Excel操作 - 自动提取`;
        
        excelOperations.push({
          operation_type: 'excel_operation',
          description: description,
          js_code: excelCode
        });
        
        // 从响应中移除代码
        cleanResponse = cleanResponse.replace(match[0], '');
      }
    }
    
    return {
      cleanResponse: cleanResponse.trim(),
      excelOperations
    };
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setError(null);
    addMessage('user', userMessage);
    setIsLoading(true);

    try {
      // 1. 读取当前活动工作表全部内容
      let markdownTable = '';
      if (typeof Excel !== 'undefined') {
        await Excel.run(async (context) => {
          const sheet = context.workbook.worksheets.getActiveWorksheet();
          const usedRange = sheet.getUsedRange();
          usedRange.load('values');
          await context.sync();
          const values = usedRange.values;
          markdownTable = arrayToMarkdownTable(values);
        });
      }
      // 2. 拼接 Markdown 表格和用户消息
      let prompt = userMessage;
      if (markdownTable && markdownTable.trim().length > 0) {
        prompt = `当前表格内容如下（Markdown 格式）：\n${markdownTable}\n\n用户问题：${userMessage}`;
      }
      // 3. 发送拼接后的 prompt
      const response = await fetch(API_ENDPOINTS.AGENT_CHAT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: prompt,
          conversation_id: `conv_${Date.now()}`,
        }),
      });
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('认证失败，请重新登录');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      if (result.success) {
        // 从AI回复中提取Excel代码
        const { cleanResponse, excelOperations } = extractExcelCodeFromResponse(result.response);
        addMessage('agent', cleanResponse, excelOperations);
      } else {
        addMessage('agent', result.response || '抱歉，处理您的请求时出现了问题。', [], result.error);
      }
    } catch (err) {
      console.error('发送消息失败:', err);
      setError(`发送消息失败: ${err instanceof Error ? err.message : '未知错误'}`);
      addMessage('agent', '抱歉，无法连接到服务器，请检查网络连接或稍后重试。');
    } finally {
      setIsLoading(false);
    }
  };

  const executeExcelOperation = async (operation: ExcelOperation, operationId: string) => {
    if (!operation.js_code) {
      console.warn('没有可执行的 JavaScript 代码');
      return;
    }

    setExecutionStatus(prev => ({ ...prev, [operationId]: 'executing' }));

    try {
      const jsCode = operation.js_code;
      const allowedPatterns = [
        /Excel\.run/,
        /context\.workbook/,
        /getRange/,
        /charts\.add/,
        /getItem/,
        /load/,
        /sync/
      ];
      
      const forbiddenPatterns = [
        /document\./,
        /window\./,
        /fetch\(/,
        /XMLHttpRequest/,
        /eval\(/,
        /Function\(/
      ];

      const hasAllowedPattern = allowedPatterns.some(pattern => pattern.test(jsCode));
      const hasForbiddenPattern = forbiddenPatterns.some(pattern => pattern.test(jsCode));

      if (!hasAllowedPattern || hasForbiddenPattern) {
        throw new Error('代码安全检查失败：包含不允许的操作');
      }

      await Excel.run(async (context) => {
        try {
          const executeCode = new Function('context', 'Excel', jsCode);
          const result = await executeCode(context, Excel);
          
          console.log('Excel 操作执行成功:', result);
          setExecutionStatus(prev => ({ ...prev, [operationId]: 'success' }));
        } catch (execError) {
          console.error('Excel 代码执行失败:', execError);
          throw execError;
        }
      });
      
    } catch (err) {
      console.error('执行 Excel 操作失败:', err);
      setExecutionStatus(prev => ({ ...prev, [operationId]: 'error' }));
      setError(`执行操作失败: ${err instanceof Error ? err.message : '未知错误'}`);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };


  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'executing':
        return <Spinner size="tiny" />;
      case 'success':
        return <CheckmarkCircle24Regular style={{ color: tokens.colorPaletteGreenForeground1 }} />;
      case 'error':
        return <ErrorCircle24Regular style={{ color: tokens.colorPaletteRedForeground1 }} />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'executing':
        return '执行中...';
      case 'success':
        return '执行成功';
      case 'error':
        return '执行失败';
      default:
        return '待执行';
    }
  };

  return (
    <div className={styles.root}>
      {error && (
        <MessageBar intent="error" className={styles.errorMessage}>
          {error}
        </MessageBar>
      )}

      <div className={styles.chatContainer}>
        <div className={styles.messagesArea}>
          {messages.length === 0 && (
            <div className={styles.emptyState}>
              <Bot24Regular className={styles.emptyStateIcon} />
              <Text>开始与 AI 助手对话，让它帮您处理 Excel 任务！</Text>
            </div>
          )}
          
          {messages.map((message) => (
            <div key={message.id}>
              {message.type === 'user' ? (
                <div className={styles.userMessage}>
                  <Text as="p" className={styles.messageText}>{message.content}</Text>
                </div>
              ) : (
                <div className={mergeClasses(styles.message, styles.agentMessageContainer)}>
                  <Bot24Regular className={styles.avatar} />
                  
                  <div className={styles.messageContent}>
                    <Text as="p" className={styles.messageText}>{message.content}</Text>
                    
                    {message.operations && message.operations.length > 0 && (
                      <div className={styles.operationsContainer}>
                        {message.operations.map((operation, index) => {
                          const operationId = `${message.id}_${index}`;
                          const status = executionStatus[operationId] || 'pending';
                          
                          return (
                            <Card key={index} className={styles.operationCard}>
                              <div className={styles.operationHeader}>
                                <Text className={styles.operationTitle}>
                                  {operation.operation_type}
                                </Text>
                              </div>
                              
                              <pre className={styles.codeBlock}>
                                {operation.js_code?.trim()}
                              </pre>
                              
                              <div className={styles.operationActions}>
                                <Button
                                  appearance="outline"
                                  className={styles.executeButton}
                                  size="small"
                                  onClick={() => executeExcelOperation(operation, operationId)}
                                  disabled={!operation.js_code || status === 'executing'}
                                >
                                  执行代码
                                </Button>
                                
                                {operation.js_code && (
                                  <Button
                                    appearance="outline"
                                    size="small"
                                    onClick={() => copyToClipboard(operation.js_code!)}
                                  >
                                    复制
                                  </Button>
                                )}
                              </div>
                            </Card>
                          );
                        })}
                      </div>
                    )}
                    
                    {message.error && (
                      <MessageBar intent="error" style={{ marginTop: '8px' }}>
                        错误: {message.error}
                      </MessageBar>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className={styles.message}>
              <Bot24Regular className={styles.avatar} />
              <div className={styles.loadingContainer}>
                <Spinner size="tiny" />
                <Text>AI 正在思考...</Text>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <div className={styles.inputContainer}>
            <Textarea
              className={styles.inputField}
              placeholder="数据你需要如何处理"
              value={inputValue}
              onChange={(_, data) => setInputValue(data.value)}
              onKeyDown={handleKeyPress}
              rows={1}
              resize="vertical"
              disabled={isLoading}
            />
            <div className={styles.sendButtonContainer}>
              <Button
                appearance="primary"
                icon={<Send24Regular style={{ color: tokens.colorNeutralBackground1 }} />}
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading}
                style={{
                  background: "transparent",
                  border: "none",
                  color: tokens.colorNeutralBackground1,
                  padding: 0,
                  minWidth: "auto",
                  width: "100%",
                  height: "100%",
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChat; 
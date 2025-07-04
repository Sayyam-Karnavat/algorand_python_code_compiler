import React, { useState, useEffect, useRef } from "react";
import {
  IconButton,
  TextField,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  CssBaseline
} from "@mui/material";
import { Delete, Add, Feedback, PlayArrow, RocketLaunch } from "@mui/icons-material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import axios from "axios";

export default function FileManager() {
  const [darkMode, setDarkMode] = useState(false);
  useEffect(() => {
    const root = document.documentElement;
    darkMode ? root.classList.add("dark") : root.classList.remove("dark");
  }, [darkMode]);

  const theme = React.useMemo(
    () => createTheme({ palette: { mode: darkMode ? "dark" : "light" } }),
    [darkMode]
  );

  const [files, setFiles] = useState([
    {
      name: "sample_contract.py",
      content: `from algopy import ARC4Contract, arc4

class HelloWorldContract(ARC4Contract):
    @arc4.abimethod
    def hello(self, name: arc4.String) -> arc4.String:
        return "Hello, " + name`
    }
  ]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [newFileName, setNewFileName] = useState("");
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedbackComment, setFeedbackComment] = useState("");

  // Output panel height state
  const [outputHeight, setOutputHeight] = useState(200);
  const startY = useRef(0);
  const startHeight = useRef(0);
  const resizerRef = useRef(null);

  const onMouseMove = (e) => {
    const dy = startY.current - e.clientY;
    setOutputHeight(Math.max(100, startHeight.current + dy));
  };

  const onMouseUp = () => {
    document.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("mouseup", onMouseUp);
  };

  const onMouseDown = (e) => {
    startY.current = e.clientY;
    startHeight.current = outputHeight;
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  const handleAddFile = () => {
    if (!newFileName.trim()) return;
    const fileName = newFileName.endsWith(".py") ? newFileName : `${newFileName}.py`;
    setFiles([...files, { name: fileName, content: "" }]);
    setSelectedIndex(files.length);
    setNewFileName("");
  };

  const handleDeleteFile = (index) => {
    if (files.length === 1) return alert("Cannot delete the last file.");
    setFiles(files.filter((_, i) => i !== index));
    setSelectedIndex((prev) => (prev === index ? 0 : prev > index ? prev - 1 : prev));
  };

  const handleCodeChange = (newCode) => {
    const updated = [...files];
    updated[selectedIndex].content = newCode;
    setFiles(updated);
  };

  const formatOutput = (text) => {
    try {
      return JSON.stringify(JSON.parse(text), null, 2);
    } catch {
      return text;
    }
  };

  const runCode = async () => {
    const code = files[selectedIndex].content;
    if (!code.trim()) return setOutput("No code to run.");
    setIsRunning(true);
    try {
      const res = await axios.post("https://algorand-python-code-compiler.onrender.com/run", { code });
      setOutput(formatOutput(res.data.output || res.data.error));
    } catch (err) {
      setOutput(`Error running code: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const deployCode = async () => {
    const { name, content } = files[selectedIndex];
    if (!content.trim()) return setOutput("No code to deploy.");
    setIsDeploying(true);
    try {
      const res = await axios.post("https://algorand-python-code-compiler.onrender.com/deploy", { file_path: name, code: content });
      const msg = res.data.message
        ? `${res.data.message}: ${JSON.stringify(res.data.deploy_result)}`
        : `Error: ${res.data.error}`;
      setOutput(formatOutput(msg));
    } catch (err) {
      setOutput(`Error deploying code: ${err.message}`);
    } finally {
      setIsDeploying(false);
    }
  };

  const submitFeedback = () => {
    console.log("Feedback:", feedbackComment);
    setFeedbackComment("");
    setFeedbackOpen(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="flex h-screen dark:bg-gray-900 bg-white">

        {/* Sidebar */}
        <div className="w-64 p-4 shadow-lg dark:bg-gray-800 bg-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl text-gray-900 dark:text-gray-100">📁 My Files</h2>
            <Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />
          </div>
          <div className="flex gap-2 mb-4">
            <TextField
              size="small"
              variant="outlined"
              label="New File"
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddFile()}
              className="flex-1"
            />
            <Tooltip title="Add New File">
              <IconButton color="primary" onClick={handleAddFile}>
                <Add />
              </IconButton>
            </Tooltip>
          </div>
          <ul className="space-y-2">
            {files.map((f, i) => (
              <li
                key={f.name + i}
                onClick={() => setSelectedIndex(i)}
                className={`flex justify-between items-center p-2 rounded cursor-pointer ${
                  i === selectedIndex
                    ? "bg-blue-200 dark:bg-blue-700"
                    : "hover:bg-blue-100 dark:hover:bg-blue-600"
                }`}
              >
                <span className="text-gray-900 dark:text-gray-100">{f.name}</span>
                <IconButton size="small" color="error" onClick={() => handleDeleteFile(i)}>
                  <Delete fontSize="small" />
                </IconButton>
              </li>
            ))}
          </ul>
        </div>

        {/* Main */}
        <div className="flex-1 flex flex-col p-6">
          <div className="flex justify-between items-center mb-4 border-b dark:border-gray-700 border-gray-300">
            <h1 className="text-2xl text-gray-900 dark:text-gray-100">
              {files[selectedIndex]?.name || "No file"}
            </h1>
            <Tooltip title="Feedback">
              <IconButton color="primary" onClick={() => setFeedbackOpen(true)}>
                <Feedback />
              </IconButton>
            </Tooltip>
          </div>

          {/* Editor */}
          <AceEditor
            mode="python"
            theme="monokai"
            value={files[selectedIndex]?.content || ""}
            onChange={handleCodeChange}
            name="editor"
            width="100%"
            height={`calc(100vh - ${outputHeight + 200}px)`} // adjust for header/buttons/output
            setOptions={{ showLineNumbers: true, tabSize: 4 }}
            className="rounded border dark:border-gray-700 border-gray-300 mb-4"
          />

          {/* Actions */}
          <div className="flex gap-2 mb-2">
            <Button variant="contained" startIcon={<PlayArrow />} onClick={runCode} disabled={isRunning}>
              {isRunning ? "Running..." : "Run"}
            </Button>
            <Button variant="contained" startIcon={<RocketLaunch />} onClick={deployCode} disabled={isDeploying}>
              {isDeploying ? "Deploying..." : "Deploy"}
            </Button>
          </div>

          {/* Resizer */}
          <div
            ref={resizerRef}
            onMouseDown={onMouseDown}
            className="h-1 bg-gray-400 dark:bg-gray-600 cursor-row-resize mb-2"
          />

          {/* Output Panel */}
          <div
            className="bg-black text-green-400 p-3 rounded font-mono overflow-y-auto"
            style={{ height: outputHeight, width: 1000, maxWidth: '100%' }}
          >
            <pre>{output || 'Output will appear here...'}</pre>
          </div>
        </div>

        {/* Feedback Dialog */}
        <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)} fullWidth maxWidth="sm">
          <DialogTitle>Submit Feedback</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Your comments"
              fullWidth
              multiline
              minRows={3}
              value={feedbackComment}
              onChange={(e) => setFeedbackComment(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFeedbackOpen(false)}>Cancel</Button>
            <Button onClick={submitFeedback} variant="contained">
              Submit
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    </ThemeProvider>
  );
}
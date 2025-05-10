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

}

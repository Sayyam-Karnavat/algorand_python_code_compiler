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
}
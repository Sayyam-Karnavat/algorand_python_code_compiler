import React, { useState, useRef, useEffect } from 'react';
import {
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Chip,
  Typography,
  TextField,
  Button
} from '@mui/material';
import {
  Clear,
  ContentCopy,
  Save,
  Download,
  Terminal,
  KeyboardArrowUp,
  KeyboardArrowDown,
  Settings,
  FilterList,
  Search
} from '@mui/icons-material';

const TerminalOutput = ({ 
  output, 
  setOutput, 
  height, 
  onHeightChange,
  isRunning,
  onInteractiveInput 
}) => {
  const [terminalHistory, setTerminalHistory] = useState([]);
  const [currentHistoryIndex, setCurrentHistoryIndex] = useState(-1);
  const [terminalInput, setTerminalInput] = useState('');
  const [isInteractive, setIsInteractive] = useState(false);
  const [filterLevel, setFilterLevel] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showSearch, setShowSearch] = useState(false);
  const [terminalSettings, setTerminalSettings] = useState({
    fontSize: 14,
    fontFamily: 'monospace',
    showTimestamps: true,
    autoScroll: true,
    maxLines: 1000
  });

  const terminalRef = useRef(null);
  const inputRef = useRef(null);
  const startY = useRef(0);
  const startHeight = useRef(0);

  useEffect(() => {
    if (terminalSettings.autoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output, terminalSettings.autoScroll]);

  const onMouseMove = (e) => {
    const dy = startY.current - e.clientY;
    onHeightChange(Math.max(100, Math.min(600, startHeight.current + dy)));
  };

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  const onMouseDown = (e) => {
    startY.current = e.clientY;
    startHeight.current = height;
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  const parseOutput = (text) => {
    if (!text) return [];
    
    const lines = text.split('\n');
    return lines.map((line, index) => {
      let type = 'info';
      if (line.toLowerCase().includes('error') || line.toLowerCase().includes('exception')) {
        type = 'error';
      } else if (line.toLowerCase().includes('warning')) {
        type = 'warning';
      } else if (line.toLowerCase().includes('success') || line.toLowerCase().includes('completed')) {
        type = 'success';
      }

      return {
        id: index,
        text: line,
        type,
        timestamp: new Date().toISOString()
      };
    });
  };

  const filteredOutput = () => {
    const parsed = parseOutput(output);
    let filtered = parsed;

    if (filterLevel !== 'all') {
      filtered = parsed.filter(line => line.type === filterLevel);
    }

    if (searchTerm) {
      filtered = filtered.filter(line => 
        line.text.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  };

  const handleClearOutput = () => {
    setOutput('');
  };

  const handleCopyOutput = () => {
    navigator.clipboard.writeText(output);
  };

  const handleSaveOutput = () => {
    const blob = new Blob([output], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `output_${new Date().toISOString().slice(0, 19)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleTerminalInput = (e) => {
    if (e.key === 'Enter') {
      const command = terminalInput.trim();
      if (command) {
        setTerminalHistory([...terminalHistory, command]);
        setCurrentHistoryIndex(-1);
        onInteractiveInput && onInteractiveInput(command);
        setTerminalInput('');
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (currentHistoryIndex < terminalHistory.length - 1) {
        const newIndex = currentHistoryIndex + 1;
        setCurrentHistoryIndex(newIndex);
        setTerminalInput(terminalHistory[terminalHistory.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (currentHistoryIndex > 0) {
        const newIndex = currentHistoryIndex - 1;
        setCurrentHistoryIndex(newIndex);
        setTerminalInput(terminalHistory[terminalHistory.length - 1 - newIndex]);
      } else if (currentHistoryIndex === 0) {
        setCurrentHistoryIndex(-1);
        setTerminalInput('');
      }
    }
  };

  const getLineColor = (type) => {
    switch (type) {
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'success': return 'text-green-400';
      default: return 'text-green-400';
    }
  };

  return (
    <div className="flex flex-col">
      {/* Resizer */}
      <div
        onMouseDown={onMouseDown}
        className="h-1 bg-gray-400 dark:bg-gray-600 cursor-row-resize hover:bg-gray-500 transition-colors"
      />

      {/* Terminal Header */}
      <div className="flex items-center justify-between p-2 bg-gray-800 text-white">
        <div className="flex items-center gap-2">
          <Terminal fontSize="small" />
          <Typography variant="body2">Terminal Output</Typography>
          {isRunning && (
            <Chip label="Running" size="small" color="primary" />
          )}
        </div>

        <div className="flex items-center gap-1">
          <Tooltip title="Search">
            <IconButton 
              size="small" 
              onClick={() => setShowSearch(!showSearch)}
              className="text-white hover:bg-gray-700"
            >
              <Search fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Filter">
            <IconButton size="small" className="text-white hover:bg-gray-700">
              <FilterList fontSize="small" />
            </IconButton>
          </Tooltip>

          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="text-xs bg-gray-700 text-white border-gray-600 rounded px-2 py-1"
          >
            <option value="all">All</option>
            <option value="info">Info</option>
            <option value="warning">Warnings</option>
            <option value="error">Errors</option>
            <option value="success">Success</option>
          </select>

          <Tooltip title="Copy Output">
            <IconButton 
              size="small" 
              onClick={handleCopyOutput}
              className="text-white hover:bg-gray-700"
            >
              <ContentCopy fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Save Output">
            <IconButton 
              size="small" 
              onClick={handleSaveOutput}
              className="text-white hover:bg-gray-700"
            >
              <Download fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Clear Output">
            <IconButton 
              size="small" 
              onClick={handleClearOutput}
              className="
import React, { useState, useEffect } from 'react';
import {
  Drawer,
  Typography,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  TextField,
  Button,
  Tooltip,
  Badge,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  BugReport,
  Close,
  PlayArrow,
  Pause,
  Stop,
  SkipNext,
  SkipPrevious,
  Visibility,
  VisibilityOff,
  Error,
  Warning,
  Info,
  CheckCircle,
  ExpandMore,
  Add,
  Delete,
  Refresh
} from '@mui/icons-material';

const DebugPanel = ({ 
  open, 
  onClose, 
  currentFile, 
  onRunDebug,
  debugOutput,
  isDebugging 
}) => {
  const [breakpoints, setBreakpoints] = useState([]);
  const [watchList, setWatchList] = useState([]);
  const [newWatchExpression, setNewWatchExpression] = useState('');
  const [debugSettings, setDebugSettings] = useState({
    stopOnError: true,
    showWarnings: true,
    verboseOutput: false,
    autoWatch: true
  });
  const [callStack, setCallStack] = useState([]);
  const [variables, setVariables] = useState([]);
  const [debugHistory, setDebugHistory] = useState([]);

  useEffect(() => {
    // Parse debug output for errors, warnings, and info
    if (debugOutput) {
      parseDebugOutput(debugOutput);
    }
  }, [debugOutput]);

  const parseDebugOutput = (output) => {
    const lines = output.split('\n');
    const newHistory = [];
    
    lines.forEach((line, index) => {
      if (line.trim()) {
        let type = 'info';
        if (line.toLowerCase().includes('error') || line.toLowerCase().includes('exception')) {
          type = 'error';
        } else if (line.toLowerCase().includes('warning')) {
          type = 'warning';
        } else if (line.toLowerCase().includes('traceback')) {
          type = 'error';
        }

        newHistory.push({
          id: index,
          line,
          type,
          timestamp: new Date().toISOString()
        });
      }
    });

    setDebugHistory(newHistory);
  };

  const addBreakpoint = (line) => {
    const newBreakpoint = {
      id: Date.now(),
      line,
      file: currentFile?.name || 'current',
      enabled: true,
      condition: '',
      hitCount: 0
    };
    setBreakpoints([...breakpoints, newBreakpoint]);
  };

  const removeBreakpoint = (id) => {
    setBreakpoints(breakpoints.filter(bp => bp.id !== id));
  };

  const toggleBreakpoint = (id) => {
    setBreakpoints(breakpoints.map(bp => 
      bp.id === id ? { ...bp, enabled: !bp.enabled } : bp
    ));
  };

  const addWatchExpression = () => {
    if (!newWatchExpression.trim()) return;
    
    const newWatch = {
      id: Date.now(),
      expression: newWatchExpression,
      value: 'Evaluating...',
      type: 'unknown',
      enabled: true
    };
    
    setWatchList([...watchList, newWatch]);
    setNewWatchExpression('');
  };

  const removeWatchExpression = (id) => {
    setWatchList(watchList.filter(w => w.id !== id));
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'error': return <Error color="error" fontSize="small" />;
      case 'warning': return <Warning color="warning" fontSize="small" />;
      case 'success': return <CheckCircle color="success" fontSize="small" />;
      default: return <Info color="info" fontSize="small" />;
    }
  };

  const getMessageCount = (type) => {
    return debugHistory.filter(item => item.type === type).length;
  };

  const mockVariables = [
    { name: 'x', value: '42', type: 'int', scope: 'local' },
    { name: 'name', value: '"Hello World"', type: 'str', scope: 'local' },
    { name: 'items', value: '[1, 2, 3, 4]', type: 'list', scope: 'local' },
    { name: '__name__', value: '"__main__"', type: 'str', scope: 'global' }
  ];

  const mockCallStack = [
    { function: 'main()', file: 'app.py', line: 15 },
    { function: 'process_data()', file: 'app.py', line: 8 },
    { function: 'validate_input()', file: 'utils.py', line: 23 }
  ];

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: 400, backgroundColor: 'background.paper' }
      }}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <BugReport color="primary" />
            <Typography variant="h6">Debug Panel</Typography>
          </div>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </div>

        {/* Debug Controls */}
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded">
          <Typography variant="subtitle2" className="mb-2">Debug Controls</Typography>
          <div className="flex gap-2 mb-3">
            <Tooltip title="Start Debug">
              <IconButton 
                color="primary" 
                onClick={onRunDebug}
                disabled={isDebugging}
                size="small"
              >
                <PlayArrow />
              </IconButton>
            </Tooltip>
            <Tooltip title="Pause">
              <IconButton color="warning" size="small" disabled={!isDebugging}>
                <Pause />
              </IconButton>
            </Tooltip>
            <Tooltip title="Stop">
              <IconButton color="error" size="small" disabled={!isDebugging}>
                <Stop />
              </IconButton>
            </Tooltip>
            <Tooltip title="Step Over">
              <IconButton size="small" disabled={!isDebugging}>
                <SkipNext />
              </IconButton>
            </Tooltip>
            <Tooltip title="Step Into">
              <IconButton size="small" disabled={!isDebugging}>
                <SkipPrevious />
              </IconButton>
            </Tooltip>
          </div>

          {/* Debug Settings */}
          <div className="space-y-1">
            <FormControlLabel
              control={
                <Switch
                  checked={debugSettings.stopOnError}
                  onChange={(e) => setDebugSettings({
                    ...debugSettings,
                    stopOnError: e.target.checked
                  })}
                  size="small"
                />
              }
              label="Stop on Error"
              className="text-sm"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={debugSettings.verboseOutput}
                  onChange={(e) => setDebugSettings({
                    ...debugSettings,
                    verboseOutput: e.target.checked
                  })}
                  size="small"
                />
              }
              label="Verbose Output"
              className="text-sm"
            />
          </div>
        </div>

        {/* Debug Status */}
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900 rounded">
          <div className="flex justify-between items-center mb-2">
            <Typography variant="subtitle2">Debug Status</Typography>
            <Chip 
              label={isDebugging ? "Running" : "Stopped"} 
              color={isDebugging ? "success" : "default"}
              size="small"
            />
          </div>
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-1">
              <Error color="error" fontSize="small" />
              <Badge badgeContent={getMessageCount('error')} color="error">
                <span>Errors</span>
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              <Warning color="warning" fontSize="small" />
              <Badge badgeContent={getMessageCount('warning')} color="warning">
                <span>Warnings</span>
              </Badge>
            </div>
          </div>
        </div>

        {/* Breakpoints */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle2">
              Breakpoints ({breakpoints.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <div className="space-y-2">
              <div className="flex gap-2">
                <TextField
                  size="small"
                  placeholder="Line number"
                  type="number"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.target.value) {
                      addBreakpoint(parseInt(e.target.value));
                      e.target.value = '';
                    }
                  }}
                  className="flex-1"
                />
                <Button size="small" startIcon={<Add />}>
                  Add
                </Button>
              </div>
              
              <List dense>
                {breakpoints.map((bp) => (
                  <ListItem
                    key={bp.id}
                    secondaryAction={
                      <div className="flex gap-1">
                        <IconButton
                          size="small"
                          onClick={() => toggleBreakpoint(bp.id)}
                        >
                          {bp.enabled ? <Visibility /> : <VisibilityOff />}
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => removeBreakpoint(bp.id)}
                        >
                          <Delete />
                        </IconButton>
                      </div>
                    }
                  >
                    <ListItemText
                      primary={`Line ${bp.line}`}
                      secondary={`${bp.file} • Hits: ${bp.hitCount}`}
                      className={bp.enabled ? '' : 'opacity-50'}
                    />
                  </ListItem>
                ))}
              </List>
              
              {breakpoints.length === 0 && (
                <Typography variant="body2" className="text-gray-500 text-center py-2">
                  No breakpoints set
                </Typography>
              )}
            </div>
            
    </AccordionDetails>
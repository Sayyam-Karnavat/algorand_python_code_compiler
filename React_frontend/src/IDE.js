import React, { useState, useRef, useEffect } from 'react';
import {
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  Divider
} from '@mui/material';
import {
  FormatSize,
  FindReplace,
  Code,
  Settings,
  Fullscreen,
  FullscreenExit,
  BookmarkBorder,
  Bookmark,
  BugReport
} from '@mui/icons-material';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/theme-github';
import 'ace-builds/src-noconflict/theme-tomorrow_night';
import 'ace-builds/src-noconflict/theme-solarized_light';
import 'ace-builds/src-noconflict/ext-language_tools';
import 'ace-builds/src-noconflict/ext-searchbox';

const CodeEditor = ({ 
  file, 
  onCodeChange, 
  darkMode,
  height 
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [theme, setTheme] = useState(darkMode ? 'monokai' : 'github');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [bookmarks, setBookmarks] = useState([]);
  const [findReplaceOpen, setFindReplaceOpen] = useState(false);
  const [editorSettings, setEditorSettings] = useState({
    showLineNumbers: true,
    showGutter: true,
    highlightActiveLine: true,
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
    enableSnippets: true,
    tabSize: 4,
    useSoftTabs: true,
    wrap: false,
    showPrintMargin: true,
    printMarginColumn: 80
  });

  const editorRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    setTheme(darkMode ? 'monokai' : 'github');
  }, [darkMode]);

  const handleFullscreen = () => {
    if (!isFullscreen) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleBookmark = () => {
    const editor = editorRef.current?.editor;
    if (!editor) return;

    const cursor = editor.getCursorPosition();
    const line = cursor.row + 1;
    const content = editor.session.getLine(cursor.row);
    
    const existingBookmark = bookmarks.find(b => b.line === line);
    if (existingBookmark) {
      setBookmarks(bookmarks.filter(b => b.line !== line));
    } else {
      setBookmarks([...bookmarks, {
        line,
        content: content.trim(),
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const jumpToBookmark = (line) => {
    const editor = editorRef.current?.editor;
    if (!editor) return;
    
    editor.gotoLine(line, 0, true);
    editor.focus();
  };

  const formatCode = () => {
    // Basic Python formatting - in a real app, you'd use a proper formatter
    const editor = editorRef.current?.editor;
    if (!editor) return;

    const code = editor.getValue();
    const formatted = code
      .split('\n')
      .map(line => line.trimRight())
      .join('\n');
    
    editor.setValue(formatted);
    editor.clearSelection();
  };

  const insertSnippet = (snippet) => {
    const editor = editorRef.current?.editor;
    if (!editor) return;

    const snippets = {
      'class': 'class ClassName:\n    def __init__(self):\n        pass\n',
      'def': 'def function_name():\n    pass\n',
      'if': 'if condition:\n    pass\n',
      'for': 'for item in iterable:\n    pass\n',
      'try': 'try:\n    pass\nexcept Exception as e:\n    pass\n',
      'main': 'if __name__ == "__main__":\n    pass\n'
    };

    if (snippets[snippet]) {
      editor.insert(snippets[snippet]);
    }
  };

  const themes = [
    { value: 'monokai', label: 'Monokai' },
    { value: 'github', label: 'GitHub' },
    { value: 'tomorrow_night', label: 'Tomorrow Night' },
    { value: 'solarized_light', label: 'Solarized Light' }
  ];

  return (
    <div ref={containerRef} className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-white dark:bg-gray-900' : ''}`}>
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between p-2 border-b dark:border-gray-600 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <Chip 
            label={file?.name || 'Untitled'} 
            size="small" 
            icon={<Code />}
            className="text-xs"
          />
          <Typography variant="caption" className="text-gray-500">
            Line {editorRef.current?.editor?.getCursorPosition()?.row + 1 || 1}
          </Typography>
        </div>
        
        <div className="flex items-center gap-1">
          <Tooltip title="Find & Replace">
            <IconButton size="small" onClick={() => setFindReplaceOpen(true)}>
              <FindReplace fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Toggle Bookmark">
            <IconButton size="small" onClick={handleBookmark}>
              {bookmarks.some(b => b.line === (editorRef.current?.editor?.getCursorPosition()?.row + 1)) ? 
                <Bookmark fontSize="small" color="primary" /> : 
                <BookmarkBorder fontSize="small" />
              }
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Format Code">
            <IconButton size="small" onClick={formatCode}>
              <FormatSize fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Settings">
            <IconButton size="small" onClick={() => setSettingsOpen(true)}>
              <Settings fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
            <IconButton size="small" onClick={handleFullscreen}>
              {isFullscreen ? <FullscreenExit fontSize="small" /> : <Fullscreen fontSize="small" />}
            </IconButton>
          </Tooltip>
        </div>
      </div>

      {/* Code Editor */}
      <AceEditor
        ref={editorRef}
        mode="python"
        theme={theme}
        value={file?.content || ''}
        onChange={onCodeChange}
        name="code-editor"
        width="100%"
        height={isFullscreen ? 'calc(100vh - 60px)' : height}
        fontSize={fontSize}
        setOptions={{
          ...editorSettings,
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true
        }}
        commands={[
          {
            name: 'formatCode',
            bindKey: { win: 'Ctrl-Shift-F', mac: 'Cmd-Shift-F' },
            exec: formatCode
          },
          {
            name: 'toggleBookmark',
            bindKey: { win: 'Ctrl-F2', mac: 'Cmd-F2' },
            exec: handleBookmark
          }
        ]}
        className="border-0"
      />

      {/* Bookmarks Panel */}
      {bookmarks.length > 0 && (
        <div className="absolute top-16 right-4 w-64 bg-white dark:bg-gray-800 shadow-lg rounded border">
          <div className="p-2 border-b dark:border-gray-600">
            <Typography variant="subtitle2">Bookmarks</Typography>
          </div>
          <div className="max-h-40 overflow-y-auto">
            {bookmarks.map((bookmark, index) => (
              <div
                key={index}
                onClick={() => jumpToBookmark(bookmark.line)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b dark:border-gray-600"
              >
                <div className="text-sm font-mono">Line {bookmark.line}</div>
                <div className="text-xs text-gray-500 truncate">{bookmark.content}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editor Settings</DialogTitle>
        <DialogContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Theme</label>
              <select 
                value={theme} 
                onChange={(e) => setTheme(e.target.value)}
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
              >
                {themes.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Font Size</label>
              <input
                type="range"
                min="10"
                max="24"
                value={fontSize}
                onChange={(e) => setFontSize(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-gray-500">{fontSize}px</span>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Tab Size</label>
              <input
                type="number"
                min="2"
                max="8"
                value={editorSettings.tabSize}
                onChange={(e) => setEditorSettings({...editorSettings, tabSize: Number(e.target.value)})}
                className="w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
              />
            </div>

            <Divider />

            <div className="space-y-2">
              {Object.entries(editorSettings).map(([key, value]) => {
                if (typeof value === 'boolean') {
                  return (
                    <label key={key} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => setEditorSettings({
                          ...editorSettings,
                          [key]: e.target.checked
                        })}
                      />
                      <span className="text-sm capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                    </label>
                  );
                }
                return null;
              })}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Code Snippets Menu */}
      <div className="absolute bottom-4 right-4">
        <div className="bg-white dark:bg-gray-800 shadow-lg rounded p-2 space-y-1">
          <Typography variant="caption" className="text-gray-500 block">Quick Snippets</Typography>
          {['class', 'def', 'if', 'for', 'try', 'main'].map(snippet => (
            <button
              key={snippet}
              onClick={() => insertSnippet(snippet)}
              className="block w-full text-left px-2 py-1 text-xs hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              {snippet}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
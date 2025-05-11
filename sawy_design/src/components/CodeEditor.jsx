import { useState, useEffect } from 'react';
import { X, Play, Save, Upload, ChevronDown, Settings, Copy, Terminal, Split, Maximize2, PanelLeft, PanelRight } from 'lucide-react';

export default function CodeEditor() {
  const [files, setFiles] = useState([
    { id: 1, name: 'index.html', active: false, language: 'html' },
    { id: 2, name: 'sample.php', active: false, language: 'php' },
    { id: 3, name: 'test.js', active: true, language: 'javascript' },
  ]);
  
  const [code, setCode] = useState(`// JavaScript Code Example
function greet(name) {
  console.log(\`Welcome to 30 Days of JavaScript!\`);
  console.log(\`Hello \${name}\`);
}

// Try calling the function
greet("World");`);

  const [output, setOutput] = useState('');
  const [theme, setTheme] = useState('dark');
  const [fontSize, setFontSize] = useState(14);
  const [showOutput, setShowOutput] = useState(true);
  const [outputHeight, setOutputHeight] = useState(150);
  const [isResizing, setIsResizing] = useState(false);
  const [layout, setLayout] = useState('vertical'); // vertical or horizontal
  
  // Set active tab
  const setActiveTab = (id) => {
    setFiles(files.map(file => ({
      ...file,
      active: file.id === id
    })));
  };

  // Close tab
  const closeTab = (id, e) => {
    e.stopPropagation();
    if (files.length > 1) {
      const newFiles = files.filter(file => file.id !== id);
      // If we closed the active tab, make another one active
      if (files.find(f => f.id === id).active && newFiles.length > 0) {
        newFiles[0].active = true;
      }
      setFiles(newFiles);
    }
  };

  // Mock function to run code
  const runCode = () => {
    setOutput("Welcome to 30 Days of JavaScript!\nHello World");
  };

  // Mock function to deploy code
  const deployCode = () => {
    setOutput("Deploying code...\nDeployment successful!\nYour application is live at: https://your-app.example.com");
  };

  // Toggle theme
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  // Handle resizing of output panel
  const startResizing = () => setIsResizing(true);
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizing) {
        const container = document.getElementById('editor-container');
        const containerRect = container.getBoundingClientRect();
        
        if (layout === 'vertical') {
          const newHeight = containerRect.bottom - e.clientY;
          setOutputHeight(Math.max(50, Math.min(newHeight, containerRect.height - 100)));
        }
      }
    };
    
    const handleMouseUp = () => {
      setIsResizing(false);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, layout]);

  // Toggle layout
  const toggleLayout = () => {
    setLayout(layout === 'vertical' ? 'horizontal' : 'vertical');
  };

  return (
    <div className={`flex flex-col w-full h-full rounded-md overflow-hidden border border-gray-700 ${theme === 'dark' ? 'bg-gray-900 text-gray-200' : 'bg-white text-gray-800'}`}>
      {/* Top Bar */}
      <div className="flex justify-between items-center px-2 py-1 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-1 rounded bg-blue-600 text-white text-xs font-bold">EDITOR</span>
          <button className="p-1 hover:bg-gray-700 rounded" onClick={toggleLayout}>
            {layout === 'vertical' ? <Split size={16} /> : <Split size={16} className="transform rotate-90" />}
          </button>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-1 hover:bg-gray-700 rounded" onClick={toggleTheme}>
            <Settings size={16} />
          </button>
          <button className="p-1 hover:bg-gray-700 rounded">
            <Maximize2 size={16} />
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex overflow-x-auto border-b border-gray-700">
        {files.map((file) => (
          <div 
            key={file.id}
            onClick={() => setActiveTab(file.id)}
            className={`flex items-center px-3 py-2 border-r border-gray-700 cursor-pointer ${
              file.active 
                ? `${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-200'} text-blue-400` 
                : `${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100'} hover:bg-gray-800`
            }`}
          >
            <span className={`mr-2 font-mono text-sm ${file.active ? 'text-blue-400' : ''}`}>{file.name}</span>
            <button 
              onClick={(e) => closeTab(file.id, e)} 
              className="p-1 rounded-full hover:bg-gray-700"
            >
              <X size={12} />
            </button>
          </div>
        ))}
        <div className="px-2 py-2 flex items-center cursor-pointer hover:bg-gray-800">
          <span className="text-lg">+</span>
        </div>
      </div>
      
      <div id="editor-container" className={`flex ${layout === 'vertical' ? 'flex-col' : 'flex-row'} flex-1 overflow-hidden`}>
        {/* Code Editor */}
        <div className={`flex-1 overflow-hidden ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
          <div className="flex h-full">
            {/* Line Numbers */}
            <div className={`py-2 px-2 text-right ${theme === 'dark' ? 'bg-gray-800 text-gray-500' : 'bg-gray-100 text-gray-400'} select-none`}>
              {Array.from({ length: code.split('\n').length }).map((_, i) => (
                <div key={i} className="font-mono text-xs">{i + 1}</div>
              ))}
            </div>
            
            {/* Code Area */}
            <textarea
              className={`flex-1 font-mono text-sm p-2 resize-none outline-none ${theme === 'dark' ? 'bg-gray-900 text-gray-300' : 'bg-white text-gray-800'}`}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              spellCheck="false"
              style={{ fontSize: `${fontSize}px` }}
            />
          </div>
        </div>
        
        {/* Resize Handle */}
        {showOutput && (
          <div 
            className={`${layout === 'vertical' ? 'cursor-row-resize h-1' : 'cursor-col-resize w-1'} ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'} hover:bg-blue-500`}
            onMouseDown={startResizing}
          ></div>
        )}
        
        {/* Output Panel */}
        {showOutput && (
          <div 
            className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'} border-t border-gray-700`}
            style={{ height: layout === 'vertical' ? `${outputHeight}px` : '100%', width: layout === 'horizontal' ? '40%' : '100%' }}
          >
            <div className="flex justify-between items-center px-3 py-1 border-b border-gray-700">
              <div className="flex items-center">
                <Terminal size={14} className="mr-2" />
                <span className="text-sm font-semibold">Output</span>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-1 rounded hover:bg-gray-700">
                  <Copy size={14} />
                </button>
                <button className="p-1 rounded hover:bg-gray-700" onClick={() => setShowOutput(false)}>
                  <X size={14} />
                </button>
              </div>
            </div>
            <pre className="p-3 font-mono text-sm whitespace-pre-wrap overflow-auto h-[calc(100%-32px)]">
              {output || "Run your code to see output here"}
            </pre>
          </div>
        )}
      </div>
      
      {/* Footer with Action Buttons */}
      <div className={`flex justify-between items-center px-4 py-2 border-t border-gray-700 ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'}`}>
        <div className="flex items-center space-x-2">
          <button 
            className="flex items-center px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
            onClick={() => setShowOutput(true)}
          >
            <Terminal size={16} className="mr-1" />
            {!showOutput ? 'Show Output' : 'Terminal'}
          </button>
        </div>
        
        <div className="flex items-center space-x-3">
          <button 
            className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium"
            onClick={runCode}
          >
            <Play size={16} className="mr-2" />
            Run
          </button>
          
          <button 
            className="flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium"
            onClick={deployCode}
          >
            <Upload size={16} className="mr-2" />
            Deploy
          </button>
        </div>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import AceEditor from 'react-ace';
import axios from 'axios';
import styled from 'styled-components';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-monokai';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background: #1e1e1e;
  color: #fff;
  font-family: 'Arial', sans-serif;
`;

const Sidebar = styled.div`
  width: 250px;
  background: #252526;
  padding: 20px;
  border-right: 1px solid #333;
`;

const EditorContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const Terminal = styled.div`
  height: 30%;
  background: #252526;
  padding: 10px;
  overflow-y: auto; /* Vertical scrolling */
  overflow-x: hidden; /* Prevent horizontal scrolling */
  white-space: pre-wrap; /* Wrap long lines with preserved whitespace */
  word-wrap: break-word; /* Break long words */
  word-break: break-all; /* Break at any character for very long strings */
  border-top: 1px solid #333;
  font-size: 14px;
  line-height: 1.5; /* Improve readability */
  max-width: 100%; /* Ensure it doesn't exceed container width */
`;

const Button = styled.button`
  background: #007acc;
  color: #fff;
  border: none;
  padding: 8px 16px;
  margin: 5px;
  cursor: pointer;
  border-radius: 4px;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  &:hover {
    background: #005fa3;
  }
  &:disabled {
    background: #555;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled.span`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
  margin-left: 8px;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const FileList = styled.ul`
  list-style: none;
  padding: 0;
`;

const FileItem = styled.li`
  padding: 8px;
  cursor: pointer;
  background: ${props => (props.active ? '#007acc' : 'transparent')};
  display: flex;
  justify-content: space-between;
  align-items: center;
  &:hover {
    background: #333;
  }
`;

const DeleteButton = styled.button`
  background: #ff4444;
  color: #fff;
  border: none;
  padding: 2px 6px;
  cursor: pointer;
  border-radius: 2px;
  &:hover {
    background: #cc0000;
  }
`;

const Input = styled.input`
  background: #333;
  color: #fff;
  border: none;
  padding: 5px;
  margin: 5px 0;
  width: 100%;
  border-radius: 4px;
`;

function App() {
  const [files, setFiles] = useState([{ name: 'sample_contract.py', content: '' }]);
  const [selectedFile, setSelectedFile] = useState(0);
  const [output, setOutput] = useState('');
  const [newFileName, setNewFileName] = useState('');
  const [showNewFileInput, setShowNewFileInput] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);

  const handleCodeChange = (newCode) => {
    const updatedFiles = [...files];
    updatedFiles[selectedFile].content = newCode;
    setFiles(updatedFiles);
  };

  const addNewFile = () => {
    setShowNewFileInput(true);
  };

  const handleNewFileSubmit = (e) => {
    if (e.key === 'Enter' && newFileName) {
      const fileName = newFileName.endsWith('.py') ? newFileName : `${newFileName}.py`;
      setFiles([...files, { name: fileName, content: '' }]);
      setSelectedFile(files.length);
      setNewFileName('');
      setShowNewFileInput(false);
    }
  };

  const deleteFile = (index) => {
    if (files.length === 1) {
      setOutput('Cannot delete the last file.');
      return;
    }
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    if (selectedFile >= updatedFiles.length) {
      setSelectedFile(updatedFiles.length - 1);
    } else if (index <= selectedFile) {
      setSelectedFile(selectedFile - 1);
    }
  };

  const formatOutput = (output) => {
    // If output is a JSON-like string, try to pretty-print it
    try {
      const parsed = JSON.parse(output);
      return JSON.stringify(parsed, null, 2); // Pretty-print with 2-space indentation
    } catch {
      // If not JSON, return as-is with preserved newlines
      return output;
    }
  };

  const runCode = async () => {
    const currentFileContent = files[selectedFile].content;
    if (!currentFileContent) {
      setOutput('No code to run in the selected file.');
      return;
    }
    setIsRunning(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/run', {
        code: currentFileContent,
      });
      setOutput(formatOutput(response.data.output || response.data.error));
    } catch (error) {
      setOutput(formatOutput('Error running code: ' + error.message));
    } finally {
      setIsRunning(false);
    }
  };

  const deployCode = async () => {
    const currentFileContent = files[selectedFile].content;
    const currentFileName = files[selectedFile].name;
    if (!currentFileContent) {
      setOutput('No code to deploy in the selected file.');
      return;
    }
    setIsDeploying(true);
    try {
      // https://algorand-python-code-compiler.vercel.app
      const response = await axios.post('http://127.0.0.1:5000/deploy', {
        file_path: currentFileName,
        code: currentFileContent,
      });
      setOutput(
        formatOutput(
          response.data.message
            ? `${response.data.message}: ${JSON.stringify(response.data.deploy_result)}`
            : `Error: ${response.data.error}`
        )
      );
    } catch (error) {
      setOutput(formatOutput('Error deploying code: ' + error.message));
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <AppContainer>
      <Sidebar>
        <h3>Files</h3>
        <Button onClick={addNewFile}>New File</Button>
        {showNewFileInput && (
          <Input
            type="text"
            placeholder="Enter file name (e.g., script.py)"
            value={newFileName}
            onChange={(e) => setNewFileName(e.target.value)}
            onKeyDown={handleNewFileSubmit}
            autoFocus
          />
        )}
        <FileList>
          {files.map((file, index) => (
            <FileItem
              key={index}
              active={index === selectedFile}
              onClick={() => setSelectedFile(index)}
            >
              {file.name}
              <DeleteButton onClick={(e) => { e.stopPropagation(); deleteFile(index); }}>
                X
              </DeleteButton>
            </FileItem>
          ))}
        </FileList>
      </Sidebar>
      <EditorContainer>
        <div style={{ padding: '10px', background: '#1e1e1e' }}>
          <Button onClick={runCode} disabled={isRunning}>
            Run {isRunning && <LoadingSpinner />}
          </Button>
          <Button onClick={deployCode} disabled={isDeploying}>
            Deploy {isDeploying && <LoadingSpinner />}
          </Button>
        </div>
        <AceEditor
          mode="python"
          theme="monokai"
          value={files[selectedFile].content}
          onChange={handleCodeChange}
          name="code-editor"
          editorProps={{ $blockScrolling: true }}
          fontSize={16}
          style={{ flex: 1, width: '100%' }}
        />
        <Terminal>{output || 'Output will appear here...'}</Terminal>
      </EditorContainer>
    </AppContainer>
  );
}

export default App;
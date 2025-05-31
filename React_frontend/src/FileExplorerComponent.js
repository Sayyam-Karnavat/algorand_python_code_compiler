import React, { useState } from 'react';
import {
  IconButton,
  TextField,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Badge
} from '@mui/material';
import {
  Delete,
  Add,
  MoreVert,
  FileCopy,
  DriveFileRenameOutline,
  Folder,
  Code,
  Search,
  ImportExport,
  Download,
  Upload
} from '@mui/icons-material';

const FileExplorer = ({ 
  files, 
  setFiles, 
  selectedIndex, 
  setSelectedIndex, 
  onFileImport,
  onFileExport 
}) => {
  const [newFileName, setNewFileName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedFileIndex, setSelectedFileIndex] = useState(null);
  const [isRenaming, setIsRenaming] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  const handleAddFile = () => {
    if (!newFileName.trim()) return;
    const fileName = newFileName.endsWith('.py') ? newFileName : `${newFileName}.py`;
    setFiles([...files, { 
      name: fileName, 
      content: '',
      modified: false,
      created: new Date().toISOString(),
      size: 0
    }]);
    setSelectedIndex(files.length);
    setNewFileName('');
  };

  const handleDeleteFile = (index) => {
    if (files.length === 1) return alert('Cannot delete the last file.');
    setFiles(files.filter((_, i) => i !== index));
    setSelectedIndex(prev => prev === index ? 0 : prev > index ? prev - 1 : prev);
  };

  const handleDuplicateFile = (index) => {
    const originalFile = files[index];
    const newName = `${originalFile.name.replace('.py', '')}_copy.py`;
    setFiles([...files, {
      ...originalFile,
      name: newName,
      created: new Date().toISOString()
    }]);
  };

  const handleRenameFile = (index, newName) => {
    if (!newName.trim()) return;
    const fileName = newName.endsWith('.py') ? newName : `${newName}.py`;
    const updated = [...files];
    updated[index].name = fileName;
    setFiles(updated);
    setIsRenaming(null);
  };

  const handleContextMenu = (event, index) => {
    event.preventDefault();
    setContextMenu({ mouseX: event.clientX, mouseY: event.clientY });
    setSelectedFileIndex(index);
  };

  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getFileIcon = (filename) => {
    if (filename.endsWith('.py')) return <Code color="primary" />;
    return <Code />;
  };

  const getFileSize = (content) => {
    return new Blob([content]).size;
  };

  return (
    <div className="w-80 p-4 shadow-lg dark:bg-gray-800 bg-gray-100">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Folder />
          File Explorer
        </h2>
        <div className="flex gap-1">
          <Tooltip title="Import File">
            <IconButton size="small" onClick={onFileImport}>
              <Upload fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export Current File">
            <IconButton size="small" onClick={onFileExport}>
              <Download fontSize="small" />
            </IconButton>
          </Tooltip>
        </div>
      </div>

      {/* Search */}
      <div className="mb-4">
        <TextField
          size="small"
          variant="outlined"
          placeholder="Search files..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search className="mr-2 text-gray-400" fontSize="small" />
          }}
          className="w-full"
        />
      </div>

      {/* Add New File */}
      <div className="flex gap-2 mb-4">
        <TextField
          size="small"
          variant="outlined"
          label="New File"
          value={newFileName}
          onChange={(e) => setNewFileName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddFile()}
          className="flex-1"
        />
        <Tooltip title="Add New File">
          <IconButton color="primary" onClick={handleAddFile}>
            <Add />
          </IconButton>
        </Tooltip>
      </div>

      {/* File List */}
      <div className="space-y-1 max-h-96 overflow-y-auto">
        {filteredFiles.map((file, i) => {
          const originalIndex = files.findIndex(f => f === file);
          return (
            <div
              key={file.name + i}
              onClick={() => setSelectedIndex(originalIndex)}
              onContextMenu={(e) => handleContextMenu(e, originalIndex)}
              className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${
                originalIndex === selectedIndex
                  ? 'bg-blue-200 dark:bg-blue-700'
                  : 'hover:bg-blue-100 dark:hover:bg-blue-600'
              }`}
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                {getFileIcon(file.name)}
                {isRenaming === originalIndex ? (
                  <TextField
                    size="small"
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onBlur={() => {
                      handleRenameFile(originalIndex, renameValue);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleRenameFile(originalIndex, renameValue);
                      } else if (e.key === 'Escape') {
                        setIsRenaming(null);
                      }
                    }}
                    autoFocus
                    className="flex-1"
                  />
                ) : (
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-900 dark:text-gray-100 truncate">
                        {file.name}
                      </span>
                      {file.modified && (
                        <Badge color="warning" variant="dot" />
                      )}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {getFileSize(file.content)} bytes
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Context Menu */}
      <Menu
        open={contextMenu !== null}
        onClose={() => setContextMenu(null)}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={() => {
          handleDuplicateFile(selectedFileIndex);
          setContextMenu(null);
        }}>
          <ListItemIcon><FileCopy fontSize="small" /></ListItemIcon>
          <ListItemText>Duplicate</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          setRenameValue(files[selectedFileIndex]?.name.replace('.py', '') || '');
          setIsRenaming(selectedFileIndex);
          setContextMenu(null);
        }}>
          <ListItemIcon><DriveFileRenameOutline fontSize="small" /></ListItemIcon>
          <ListItemText>Rename</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          handleDeleteFile(selectedFileIndex);
          setContextMenu(null);
        }}>
          <ListItemIcon><Delete fontSize="small" /></ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* File Statistics */}
      <div className="mt-4 pt-4 border-t dark:border-gray-600">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {files.length} files • {files.reduce((acc, f) => acc + getFileSize(f.content), 0)} bytes total
        </div>
      </div>
    </div>
  );
};

export default FileExplorer;
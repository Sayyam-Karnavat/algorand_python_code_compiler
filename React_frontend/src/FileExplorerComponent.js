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
)
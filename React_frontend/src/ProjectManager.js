import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Typography,
  Card,
  CardContent,
  Grid,
  Menu,
  MenuItem
} from '@mui/material';
import {
  FolderOpen,
  Add,
  Delete,
  Edit,
  Download,
  Upload,
  Star,
  StarBorder,
  MoreVert,
  Code,
  Schedule,
  Person
} from '@mui/icons-material';

const ProjectManager = ({ 
  open, 
  onClose, 
  onLoadProject, 
  currentFiles, 
  onSaveProject 
}) => {
  const [projects, setProjects] = useState([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  useEffect(() => {
    // Load projects from localStorage
    const savedProjects = JSON.parse(localStorage.getItem('ide_projects') || '[]');
    setProjects(savedProjects);
  }, []);

  const saveProjectsToStorage = (updatedProjects) => {
    localStorage.setItem('ide_projects', JSON.stringify(updatedProjects));
    setProjects(updatedProjects);
  };

  const handleCreateProject = () => {
    if (!newProjectName.trim()) return;

    const newProject = {
      id: Date.now().toString(),
      name: newProjectName,
      description: newProjectDescription,
      files: currentFiles,
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      starred: false,
      tags: [],
      author: 'Current User'
    };

    const updatedProjects = [...projects, newProject];
    saveProjectsToStorage(updatedProjects);
    
    setNewProjectName('');
    setNewProjectDescription('');
  };

  const handleDeleteProject = (projectId) => {
    const updatedProjects = projects.filter(p => p.id !== projectId);
    saveProjectsToStorage(updatedProjects);
  };

  const handleStarProject = (projectId) => {
    const updatedProjects = projects.map(p => 
      p.id === projectId ? { ...p, starred: !p.starred } : p
    );
    saveProjectsToStorage(updatedProjects);
  };

  const handleLoadProject = (project) => {
    onLoadProject(project.files);
    onClose();
  };

  const handleUpdateProject = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    const updatedProject = {
      ...project,
      files: currentFiles,
      modified: new Date().toISOString()
    };

    const updatedProjects = projects.map(p => 
      p.id === projectId ? updatedProject : p
    );
    saveProjectsToStorage(updatedProjects);
  };

  const handleExportProject = (project) => {
    const dataStr = JSON.stringify(project, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${project.name}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImportProject = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const project = JSON.parse(e.target.result);
          project.id = Date.now().toString(); // Generate new ID
          project.imported = new Date().toISOString();
          
          const updatedProjects = [...projects, project];
          saveProjectsToStorage(updatedProjects);
        } catch (error) {
          alert('Error importing project: Invalid file format');
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  const handleContextMenu = (event, project) => {
    event.preventDefault();
    setContextMenu({ mouseX: event.clientX, mouseY: event.clientY });
    setSelectedProject(project);
  };

  const getFileCount = (files) => {
    return files ? files.length : 0;
  };

  const getTotalSize = (files) => {
    if (!files) return 0;
    return files.reduce((total, file) => total + new Blob([file.content]).size, 0);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const sortedProjects = [...projects].sort((a, b) => {
    if (a.starred && !b.starred) return -1;
    if (!a.starred && b.starred) return 1;
    return new Date(b.modified) - new Date(a.modified);
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FolderOpen />
          Project Manager
        </div>
        <div className="flex gap-2">
          <Button
            startIcon={<Upload />}
            onClick={handleImportProject}
            size="small"
          >
            Import
          </Button>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={handleCreateProject}
            disabled={!newProjectName.trim()}
            size="small"
          >
            Create
          </Button>
        </div>
      </DialogTitle>

      <DialogContent>
        {/* Create New Project */}
        <Card className="mb-4">
          <CardContent>
            <Typography variant="h6" className="mb-2">Create New Project</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Project Name"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Description (Optional)"
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  size="small"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Projects List */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <Typography variant="h6">Your Projects ({projects.length})</Typography>
            <div className="flex gap-1">
              <Button
                size="small"
                variant={viewMode === 'grid' ? 'contained' : 'outlined'}
                onClick={() => setViewMode('grid')}
              >
                Grid
              </Button>
              <Button
                size="small"
                variant={viewMode === 'list' ? 'contained' : 'outlined'}
                onClick={() => setViewMode('list')}
              >
                List
              </Button>
            </div>
          </div>

          {viewMode === 'grid' ? (
            <Grid container spacing={2}>
              {sortedProjects.map((project) => (
                <Grid item xs={12} sm={6} md={4} key={project.id}>
                  <Card 
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onContextMenu={(e) => handleContextMenu(e, project)}
                  >
                    <CardContent>
                      <div className="flex justify-between items-start mb-2">
                        <Typography variant="h6" className="truncate">
                          {project.name}
                        </Typography>
                        <IconButton
                          size="small"
                          onClick={() => handleStarProject(project.id)}
                        >
                          {project.starred ? 
                            <Star color="primary" fontSize="small" /> : 
                            <StarBorder fontSize="small" />
                          }
                        </IconButton>
                      </div>
                      
                      {project.description && (
                        <Typography variant="body2" className="text-gray-600 mb-2">
                          {project.description}
                        </Typography>
                      )}

                      <div className="flex flex-wrap gap-1 mb-2">
                        <Chip 
                          icon={<Code />} 
                          label={`${getFileCount(project.files)} files`} 
                          size="small" 
                        />
                        <Chip 
                          label={formatFileSize(getTotalSize(project.files))} 
                          size="small" 
                        />
                      </div>

                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>Modified: {new Date(project.modified).toLocaleDateString()}</span>
                        <div className="flex gap-1">
                          <Button
                            size="small"
                            onClick={() => handleLoadProject(project)}
                          >
                            Load
                          </Button>
                          <Button
                            size="small"
                            onClick={() => handleUpdateProject(project.id)}
                          >
                            Update
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <List>
              {sortedProjects.map((project) => (
                <ListItem
                  key={project.id}
                  button
                  onClick={() => handleLoadProject(project)}
                  onContextMenu={(e) => handleContextMenu(e, project)}
                >
                  <ListItemText
                    primary={
                      <div className="flex items-center gap-2">
                        {project.starred && <Star color="primary" fontSize="small" />}
                        <span>{project.name}</span>
                        <Chip 
                          label={`${getFileCount(project.files)} files`} 
                          size="small" 
                        />
                      </div>
                    }
                    secondary={
                      <div>
                        {project.description && <div>{project.description}</div>}
                        <div className="text-xs">
                          Created: {new Date(project.created).toLocaleDateString()} | 
                          Modified: {new Date(project.modified).toLocaleDateString()} |
                          Size: {formatFileSize(getTotalSize(project.files))}
                        </div>
                      </div>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton onClick={() => handleUpdateProject(project.id)}>
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteProject(project.id)}>
                      <Delete fontSize="small" />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}

          {projects.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FolderOpen style={{ fontSize: 64, opacity: 0.3 }} />
              <Typography>No projects yet. Create your first project!</Typography>
            </div>
          )}
        </div>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

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
          handleLoadProject(selectedProject);
          setContextMenu(null);
        }}>
          <FolderOpen className="mr-2" fontSize="small" />
          Load Project
        </MenuItem>
        <MenuItem onClick={() => {
          handleUpdateProject(selectedProject.id);
          setContextMenu(null);
        }}>
          <Edit className="mr-2" fontSize="small" />
          Update with Current Files
        </MenuItem>
        <MenuItem onClick={() => {
          handleStarProject(selectedProject.id);
          setContextMenu(null);
        }}>
          {selectedProject?.starred ? 
            <Star className="mr-2" fontSize="small" /> : 
            <StarBorder className="mr-2" fontSize="small" />
          }
          {selectedProject?.starred ? 'Unstar' : 'Star'}
        </MenuItem>
        <MenuItem onClick={() => {
          handleExportProject(selectedProject);
          setContextMenu(null);
        }}>
          <Download className="mr-2" fontSize="small" />
          Export Project
        </MenuItem>
        <MenuItem onClick={() => {
          handleDeleteProject(selectedProject.id);
          setContextMenu(null);
        }}>
          <Delete className="mr-2" fontSize="small" />
          Delete Project
        </MenuItem>
      </Menu>
    </Dialog>
  );
};

export default ProjectManager;
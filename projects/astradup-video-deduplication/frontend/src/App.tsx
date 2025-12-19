import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import DuplicateDetection from './pages/DuplicateDetection';
import VideoDetail from './pages/VideoDetail';
import FileRenaming from './pages/FileRenaming';
import Dashboard from './pages/Dashboard';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="detect" element={<DuplicateDetection />} />
          <Route path="rename" element={<FileRenaming />} />
          <Route path="video/:id" element={<VideoDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

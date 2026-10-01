import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import './App.css';

// Page components
import Landing from './pages/Landing/Landing';
import Classify from './pages/Classify/Classify';
import Result from './pages/Result/Result';
import Dashboard from './pages/Dashboard/Dashboard';
import History from './pages/History/History';
import Analytics from './pages/Analytics/Analytics';
import Categories from './pages/Categories/Categories';
import About from './pages/About/About';
import NotFound from './pages/NotFound/NotFound';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="classify" element={<Classify />} />
          <Route path="result/:id" element={<Result />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="history" element={<History />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="categories" element={<Categories />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import JobsPage from './pages/Jobs';
import ProfilePage from './pages/Profile';
import ScrapePage from './pages/Scrape';
import ChatPage from './pages/Chat';
import SettingsPage from './pages/Settings';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout><Dashboard /></Layout>} />
        <Route path="/jobs" element={<Layout><JobsPage /></Layout>} />
        <Route path="/profile" element={<Layout><ProfilePage /></Layout>} />
        <Route path="/scrape" element={<Layout><ScrapePage /></Layout>} />
        <Route path="/chat" element={<Layout><ChatPage /></Layout>} />
        <Route path="/documents" element={<Layout><div className="p-4">Document Manager (Coming Soon)</div></Layout>} />
        <Route path="/settings" element={<Layout><SettingsPage /></Layout>} />
      </Routes>
    </Router>
  );
}

export default App;
